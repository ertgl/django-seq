from typing import (
    Callable,
    Optional,
    Sequence,
    Union,
    cast,
)

from django.db.models import (
    F,
    Model,
)
from django.db.models.constants import LOOKUP_SEP


__all__ = (
    'Segment',
    'Key',
    'SequenceKeyEvaluator',
)


Segment = Union[
    int,
    str,
    F,
    Callable[[Model], str],
]


Key = Union[
    Segment,
    Sequence[Segment],
    Callable[[Model], Union[Segment, Sequence[Segment]]],
]


class SequenceKeyEvaluator:

    @classmethod
    def evaluate(
        cls,
        instance: Model,
        path: Optional[Key],
        separator: str = '.',
    ) -> Optional[str]:
        if path is None:
            return None
        if callable(path):
            path = path(instance)
        if isinstance(path, (tuple, list)):
            value = [
                cls.evaluate_segment(instance, segment)
                for segment in path
            ]
            path = separator.join(value)
        return cls.evaluate_segment(
            instance,
            cast(Segment, path),
        )

    @classmethod
    def evaluate_segment(
        cls,
        instance: Model,
        segment: Segment,
    ) -> str:
        if callable(segment):
            segment = segment(instance)
        if isinstance(segment, F):
            return cls.evaluate_f(instance, segment)
        return str(segment)

    @classmethod
    def evaluate_f(
        cls,
        instance: Model,
        segment: F,
    ) -> str:
        f_name_split = segment.name.split(LOOKUP_SEP)
        acc = instance
        for f_name in f_name_split:
            acc = getattr(acc, f_name)
        if isinstance(acc, Model):
            acc = acc.pk
        return str(acc)
