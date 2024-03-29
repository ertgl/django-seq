from typing import Any


__all__ = (
    'setup',
)


def setup(
    *args: Any,
    **kwargs: Any,
) -> None:
    setting = kwargs.get('setting', '')
    if setting and not setting.startswith('DJANGO_SEQ_'):
        return
    from django_seq.conf import settings
    from django_seq.connector import Connector
    settings.reload()
    Connector.handle_registry()
