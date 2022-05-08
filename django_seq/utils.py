from typing import (
    TYPE_CHECKING,
    Type,
    cast,
)

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model
from django.db.models.options import Options


if TYPE_CHECKING:
    from django_seq.models import AbstractSequence


__all__ = (
    'get_sequence_model',
    'get_model_options',
)


def _get_swappable_model(
    setting_attname: str,
    model_class_path: str,
) -> Type[Model]:
    model: Type[Model]
    try:
        model = cast(
            Type[Model],
            apps.get_model(
                model_class_path,
                require_ready=False,
            ),
        )
    except ValueError:
        raise ImproperlyConfigured(
            f"{setting_attname} must be of the form 'app_issue.model_name'",
        )
    except LookupError:
        raise ImproperlyConfigured(
            f"{setting_attname} refers to model '{model_class_path}' that has not been installed"
        )
    return model


def get_sequence_model() -> Type['AbstractSequence']:
    from django_seq.conf import settings
    return cast(
        Type['AbstractSequence'],
        _get_swappable_model(
            settings.SEQUENCE_MODEL_ATTNAME,
            settings.SEQUENCE_MODEL,
        ),
    )


def get_model_options(
    model: Type[Model],
) -> Options:
    return model._meta  # noqa
