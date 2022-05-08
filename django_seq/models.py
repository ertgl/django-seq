import datetime
from typing import (
    Any,
    Dict,
    Optional,
    Tuple,
    Union,
)

from django.db import models
from django.utils.translation import gettext_lazy as _

from django_seq._typing import (
    DateTimeField,
    PositiveBigIntegerField,
    TextField,
)
from django_seq.conf import settings
from django_seq.fields import SequenceField
from django_seq.segmentation import (
    Key,
    Segment,
    SequenceKeyEvaluator,
)
from django_seq.utils import get_sequence_model


__all__ = (
    'get_sequence_model',
    'Segment',
    'Key',
    'SequenceKeyEvaluator',
    'SequenceField',
    'AbstractSequence',
    'BaseSequence',
    'Sequence',
)


class AbstractSequence(models.Model):

    KEY_FIELD_NAME = 'key'

    VALUE_FIELD_NAME = 'value'

    CREATED_AT_FIELD_NAME = 'created_at'

    UPDATED_AT_FIELD_NAME = 'updated_at'

    class Meta:
        abstract = True

    @classmethod
    def get_or_create(
        cls,
        key: str,
        defaults: Optional[Dict[str, Any]] = None,
        select_for_update: bool = True,
        nowait: bool = False,
    ) -> Tuple['AbstractSequence', bool]:
        defaults = defaults or {
            cls.VALUE_FIELD_NAME: 0,
        }
        queryset: Union[
            'models.BaseManager[AbstractSequence]',
            'models.QuerySet[AbstractSequence]',
        ] = cls.objects
        if select_for_update:
            queryset = queryset.select_for_update(nowait=nowait)
        return queryset.get_or_create(
            defaults=defaults,
            **{
                cls.KEY_FIELD_NAME: key,
            },
        )

    @classmethod
    def get_current_value(
        cls,
        key: str,
    ) -> int:
        sequence = cls.objects.filter(
            **{
                cls.KEY_FIELD_NAME: key,
            },
        ).first()
        return getattr(sequence, cls.VALUE_FIELD_NAME, 0)

    @classmethod
    def get_next_value(
        cls,
        key: str,
        nowait: bool = False,
    ) -> int:
        sequence, is_created = cls.get_or_create(
            key,
            defaults={
                cls.VALUE_FIELD_NAME: 1,
            },
            select_for_update=True,
            nowait=nowait,
        )
        value = getattr(sequence, cls.VALUE_FIELD_NAME)
        if not is_created:
            value = value + 1
            setattr(sequence, cls.VALUE_FIELD_NAME, value)
            sequence.save()
        return value


class BaseSequence(
    AbstractSequence,
    models.Model,
):

    key: TextField[
        str,
        str,
    ] = models.TextField(
        verbose_name=_('key'),
        blank=False,
        null=False,
        unique=True,
    )

    value: PositiveBigIntegerField[
        int,
        int,
    ] = models.PositiveBigIntegerField(
        verbose_name=_('value'),
        blank=True,
        null=False,
        default=0,
    )

    created_at: DateTimeField[
        datetime.datetime,
        datetime.datetime,
    ] = models.DateTimeField(
        verbose_name=_('created at'),
        auto_now_add=True,
        blank=True,
        null=False,
        db_index=True,
    )

    updated_at: DateTimeField[
        datetime.datetime,
        datetime.datetime,
    ] = models.DateTimeField(
        verbose_name=_('updated at'),
        auto_now=True,
        blank=True,
        null=False,
        db_index=True,
    )

    class Meta:
        abstract = True


class Sequence(
    BaseSequence,
    models.Model,
):

    class Meta(BaseSequence.Meta):

        verbose_name = _('sequence')

        verbose_name_plural = _('sequences')

        swappable = settings.SEQUENCE_MODEL_ATTNAME

        db_table = 'django_seq__sequences'

        ordering = [
            AbstractSequence.KEY_FIELD_NAME,
        ]

    def __str__(self):
        return getattr(self, self.__class__.KEY_FIELD_NAME)
