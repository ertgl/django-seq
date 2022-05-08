from django.db import models

from django_seq.models import SequenceField


class Repository(models.Model):
    ...


class Issue(models.Model):

    repository = models.ForeignKey(  # type: ignore
        to=Repository,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
    )

    index = SequenceField(  # type: ignore
        key=['repositories', models.F('repository'), 'issues'],
    )

    class Meta:

        unique_together = (
            ('repository', 'index'),
        )
