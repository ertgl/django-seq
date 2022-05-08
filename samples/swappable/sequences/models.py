from django_seq.models import BaseSequence


class Sequence(BaseSequence):

    class Meta(
        BaseSequence.Meta,
    ):

        db_table = 'sequences'
