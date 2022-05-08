from contextlib import suppress
from typing import TYPE_CHECKING

from django.db import models

from django_seq._typing_ext import mimic_generic_type


__all__ = (
    'IS_MYPY_DJANGO_PLUGIN_ENABLED',
    'DateTimeField',
    'PositiveBigIntegerField',
    'TextField',
)


IS_MYPY_DJANGO_PLUGIN_ENABLED = False

with suppress(
    ImportError,
    TypeError,
):
    import mypy_django_plugin  # noqa
    if TYPE_CHECKING:
        models.Field[object, object]  # noqa
        IS_MYPY_DJANGO_PLUGIN_ENABLED = True


DateTimeField = models.DateTimeField
if not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    DateTimeField = mimic_generic_type(models.DateTimeField)  # type: ignore[misc]


PositiveBigIntegerField = models.PositiveBigIntegerField
if not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    PositiveBigIntegerField = mimic_generic_type(models.PositiveBigIntegerField)  # type: ignore[misc]


TextField = models.TextField
if not IS_MYPY_DJANGO_PLUGIN_ENABLED:
    TextField = mimic_generic_type(models.TextField)  # type: ignore[misc]
