from django.apps import AppConfig
from django.core.signals import setting_changed
from django.utils.translation import gettext_lazy as _


__all__ = (
    'DjangoSeqConfig',
)


class DjangoSeqConfig(AppConfig):

    name = 'django_seq'

    verbose_name = _('Sequences')

    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self) -> None:
        from django_seq import setup
        setup()

        setting_changed.connect(
            setup,
            dispatch_uid='django_seq.setup',
        )
