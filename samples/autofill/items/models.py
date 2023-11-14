from django.db import models

from django_seq.models import SequenceField


class Item(models.Model):

    reusable_number = SequenceField(  # type: ignore
        key=['reusable_items'],
        fill_gaps=True,
        unique=True,
    )

    unique_number = SequenceField(  # type: ignore
        key=['unique_items'],
        resolve_integrity_errors=True,
        unique=True,
    )
