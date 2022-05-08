from django.test import TestCase
from sequences.models import Sequence

from django_seq import get_sequence_model


class SequenceTestCase(TestCase):

    def test_get_sequence_model(self) -> None:
        self.assertIs(get_sequence_model(), Sequence)
