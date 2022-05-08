from typing import (
    Any,
    Optional,
)

from django import forms
from django.contrib import admin
from django.contrib.admin import widgets
from django.db import models
from django.http import HttpRequest

from django_seq.models import Sequence
from django_seq.utils import get_model_options


__all__ = (
    'SequenceAdmin',
)


class SequenceAdmin(admin.ModelAdmin):

    model = Sequence

    model_options = get_model_options(Sequence)

    list_display = (
        getattr(model_options.pk, 'name', 'pk'),
        Sequence.KEY_FIELD_NAME,
        Sequence.VALUE_FIELD_NAME,
        Sequence.CREATED_AT_FIELD_NAME,
        Sequence.UPDATED_AT_FIELD_NAME,
    )

    list_display_links = list_display

    search_fields = (
        getattr(model_options.pk, 'name', 'pk'),
        Sequence.KEY_FIELD_NAME,
    )

    list_filter = (
        Sequence.CREATED_AT_FIELD_NAME,
        Sequence.UPDATED_AT_FIELD_NAME,
    )

    fieldsets = (
        (
            None,
            {
                'fields': (
                    Sequence.KEY_FIELD_NAME,
                    Sequence.VALUE_FIELD_NAME,
                ),
            },
        ),
    )

    def formfield_for_dbfield(
        self,
        db_field: models.Field,
        request: Optional[HttpRequest],
        **kwargs: Any,
    ) -> Optional[forms.Field]:
        if db_field.name == Sequence.KEY_FIELD_NAME:
            kwargs['widget'] = widgets.AdminTextInputWidget
        return super(SequenceAdmin, self).formfield_for_dbfield(
            db_field,
            request,
            **kwargs,
        )


admin.site.register(
    Sequence,
    SequenceAdmin,
)
