from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from django.db.models import (
    F,
    Max,
    Model,
    NOT_PROVIDED,
    OuterRef,
    Q,
    Subquery,
)
from django.db.models.constants import LOOKUP_SEP

from django_seq._typing import PositiveBigIntegerField
from django_seq.segmentation import (
    Key,
    SequenceKeyEvaluator,
)
from django_seq.utils import (
    get_model_options,
    get_sequence_model,
)


__all__ = (
    'SequenceField',
)


ST = TypeVar('ST')

GT = TypeVar('GT')


class SequenceField(
    PositiveBigIntegerField[ST, GT],
):

    key: Union[
        None,
        Key,
        Type[NOT_PROVIDED],
    ]

    separator: str

    nowait: bool

    fill_gaps: bool | Callable[[Model], bool]

    resolve_integrity_errors: bool | Callable[[Model], bool]

    def __init__(
        self,
        *args,
        key: Union[
            None,
            Key,
            Type[NOT_PROVIDED],
        ] = NOT_PROVIDED,
        separator: str = '.',
        nowait: bool = False,
        fill_gaps: bool | Callable[[Model], bool] = False,
        resolve_integrity_errors: bool | Callable[[Model], bool] = False,
        blank: bool = True,
        null: bool = False,
        editable: bool = False,
        **kwargs,
    ) -> None:
        kwargs.update(
            blank=blank,
            null=null,
            editable=editable,
        )
        self.key = key
        self.separator = separator
        self.nowait = nowait
        self.fill_gaps = fill_gaps
        self.resolve_integrity_errors = resolve_integrity_errors
        super(SequenceField, self).__init__(*args, **kwargs)

    def deconstruct(self) -> Tuple[str, str, Sequence[Any], Dict[str, Any]]:
        name, key, args, kwargs = super(SequenceField, self).deconstruct()
        key = 'django_seq.models.SequenceField'
        kwargs['key'] = self.key
        kwargs['separator'] = self.separator
        kwargs['nowait'] = self.nowait
        kwargs['fill_gaps'] = self.fill_gaps
        kwargs['resolve_integrity_errors'] = self.resolve_integrity_errors
        return name, key, args, kwargs

    def handle_pre_save_signal(
        self,
        sender: Type[Model],
        instance: Model,
        **kwargs,
    ) -> bool:
        value = getattr(instance, self.name, None)
        if value is not None or self.default is not NOT_PROVIDED:
            return False

        model_options = get_model_options(sender)

        key = (
            cast(Optional[Key], self.key)
            if self.key is not NOT_PROVIDED
            else model_options.db_table
        )

        evaluated_key = SequenceKeyEvaluator.evaluate(
            instance,
            key,
            separator=self.separator,
        )

        if not evaluated_key:
            return False

        sequence_model = get_sequence_model()

        should_fill_gaps = self.fill_gaps
        if callable(should_fill_gaps):
            should_fill_gaps = should_fill_gaps(instance)

        should_resolve_integrity_errors: bool | Callable[[Model], bool] = False
        if not should_fill_gaps:
            should_resolve_integrity_errors = self.resolve_integrity_errors
            if callable(should_resolve_integrity_errors):
                should_resolve_integrity_errors = should_resolve_integrity_errors(instance)

        if should_fill_gaps:
            next_number_sub_queryset = sender.objects.order_by(
                self.name,
            ).filter(
                **{LOOKUP_SEP.join([self.name, 'gt']): OuterRef(self.name)},
            ).values(
                self.name,
            )[:1]

            gaps = sender.objects.order_by(
                self.name,
            ).annotate(
                next_number=Subquery(next_number_sub_queryset),
            ).filter(
                (
                    Q(
                        **{LOOKUP_SEP.join(['next_number', 'isnull']): True},
                    )
                    | ~Q(
                        next_number=F(self.name) + 1,
                    )
                ),
            )

            first_gap = gaps.first()

            current_value: int

            if first_gap is not None:
                current_value = getattr(first_gap, self.name)
            else:
                current_value = sender.objects.aggregate(
                    max_value=Max(
                        self.name,
                        default=0,
                        output_field=self.__class__(),
                    ),
                )['max_value']

            value = current_value + 1

            sequence_model.set_current_value(evaluated_key, value)

        elif should_resolve_integrity_errors:
            current_value = sequence_model.get_current_value(evaluated_key)

            next_number_sub_queryset = sender.objects.order_by(
                self.name,
            ).filter(
                **{LOOKUP_SEP.join([self.name, 'gt']): OuterRef(self.name)},
            ).values(
                self.name,
            )[:1]

            gaps = sender.objects.order_by(
                self.name,
            ).filter(
                **{LOOKUP_SEP.join([self.name, 'gt']): current_value},
            ).annotate(
                next_number=Subquery(next_number_sub_queryset),
            ).filter(
                (
                    Q(
                        **{LOOKUP_SEP.join(['next_number', 'isnull']): True},
                    )
                    | ~Q(
                        next_number=F(self.name) + 1,
                    )
                ),
            )

            first_gap = gaps.first()

            if first_gap is not None:
                current_value = getattr(first_gap, self.name)
            else:
                current_value = sender.objects.aggregate(
                    max_value=Max(
                        self.name,
                        default=0,
                        output_field=self.__class__(),
                    ),
                )['max_value']

            value = current_value + 1

            sequence_model.set_current_value(evaluated_key, value)

        else:
            value = sequence_model.get_next_value(
                evaluated_key,
                nowait=self.nowait,
            )

        setattr(instance, self.name, value)

        return True

    def contribute_to_class(
        self,
        model: Type[Model],
        name: str,
        private_only: bool = False,
    ) -> None:
        from django_seq.globals import registry

        registry.model_sequence_field_pairs.add((model, name, self))

        return super(SequenceField, self).contribute_to_class(
            model,
            name,
            private_only=private_only,
        )
