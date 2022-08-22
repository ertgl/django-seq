from typing import Optional, TYPE_CHECKING, Type

from django.db.models import Model, signals

from django_seq.fields import SequenceField
from django_seq.utils import get_model_options

if TYPE_CHECKING:
    from django_seq.registry import Registry


__all__ = (
    'Connector',
)


class Connector:

    @classmethod
    def handle_registry(
        cls,
        registry: Optional["Registry"] = None,
    ):
        if registry is None:
            from django_seq.globals import registry as _registry
            registry = _registry
        assert registry is not None  # noqa
        for parent_model, field_name, field in registry.model_sequence_field_pairs:
            models = [parent_model, *parent_model.__subclasses__()]
            for model in models:
                model_options = get_model_options(model)
                if model_options.abstract:
                    continue
                cls.connect_pre_save(model, field_name, field)

    @classmethod
    def connect_pre_save(
        cls,
        model: Type[Model],
        field_name: str,
        sequence_field: SequenceField
    ) -> None:
        model_options = get_model_options(model)

        signals.pre_save.connect(
            sequence_field.handle_pre_save_signal,
            sender=model,
            dispatch_uid=f'{model_options.app_label}.{model_options.label}.{field_name}.set_default_value',
        )
