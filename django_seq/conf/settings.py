from django.conf import settings


__all__ = (
    'SEQUENCE_MODEL_ATTNAME',
    'DEFAULT_SEQUENCE_MODEL',
    'SEQUENCE_MODEL',
    'reload',
)


SEQUENCE_MODEL_ATTNAME = 'DJANGO_SEQ_SEQUENCE_MODEL'

DEFAULT_SEQUENCE_MODEL = 'django_seq.Sequence'

SEQUENCE_MODEL: str


def reload() -> None:

    global SEQUENCE_MODEL
    SEQUENCE_MODEL = getattr(
        settings,
        SEQUENCE_MODEL_ATTNAME,
        None,
    ) or DEFAULT_SEQUENCE_MODEL
    if not hasattr(settings, SEQUENCE_MODEL_ATTNAME):
        setattr(settings, SEQUENCE_MODEL_ATTNAME, SEQUENCE_MODEL)


reload()
