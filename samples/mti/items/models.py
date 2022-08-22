from django.db import models

from django_seq.models import SequenceField


class Item(models.Model):

    number = SequenceField(  # type: ignore
        key=['items'],
        unique=True,
    )


class ItemA(Item):
    ...


class ItemB(Item):
    ...
