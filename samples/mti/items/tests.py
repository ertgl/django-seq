from django.test import TestCase
from items.models import (
    ItemA,
    ItemB,
)


class ItemTestCase(TestCase):

    def test_sequence_field(self) -> None:
        item_1 = ItemA.objects.create()
        self.assertEqual(item_1.number, 1)

        item_2 = ItemB.objects.create()
        self.assertEqual(item_2.number, 2)
