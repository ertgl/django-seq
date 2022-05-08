from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

from django.db.models import (
    Model,
    NOT_PROVIDED,
    signals,
)

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
        super(SequenceField, self).__init__(*args, **kwargs)

    def deconstruct(self) -> Tuple[str, str, Tuple[Any, ...], Dict[str, Any]]:
        name, key, args, kwargs = super(SequenceField, self).deconstruct()
        key = 'django_seq.models.SequenceField'
        kwargs['key'] = self.key
        kwargs['separator'] = self.separator
        kwargs['nowait'] = self.nowait
        return name, key, args, kwargs

    def _handle_pre_save_signal(
        self,
        sender: Type[Model],
        instance: Model,
        **kwargs,
    ) -> bool:

        value = getattr(instance, self.name)
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

        model_options = get_model_options(model)

        signals.pre_save.connect(
            self._handle_pre_save_signal,
            sender=model,
            dispatch_uid=f'{model_options.label}.{name}.set_default_value',
        )

        return super(SequenceField, self).contribute_to_class(
            model,
            name,
            private_only=private_only,
        )
