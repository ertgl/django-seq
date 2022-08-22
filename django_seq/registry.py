import dataclasses
from typing import Set, Tuple, Type

from django.db.models import Model

from django_seq.fields import SequenceField


__all__ = (
    'Registry',
)


@dataclasses.dataclass()
class Registry:

    model_sequence_field_pairs: Set[
        Tuple[
            Type[Model],
            str,
            SequenceField,
        ],
    ] = dataclasses.field(
        kw_only=True,
        default_factory=set,
    )
