from django.test import TestCase
from django_seq.utils import get_sequence_model

from items.models import Item


Sequence = get_sequence_model()


class ItemTestCase(TestCase):

    def test_sequence_field_fills_gaps(self) -> None:
        item_1 = Item.objects.create()
        self.assertEqual(item_1.reusable_number, 1)
        self.assertEqual(Sequence.get_current_value('reusable_items'), 1)

        item_2 = Item.objects.create()
        self.assertEqual(item_2.reusable_number, 2)
        self.assertEqual(Sequence.get_current_value('reusable_items'), 2)

        item_3 = Item.objects.create()
        self.assertEqual(item_3.reusable_number, 3)
        self.assertEqual(Sequence.get_current_value('reusable_items'), 3)

        item_3.delete()
        self.assertEqual(Sequence.get_current_value('reusable_items'), 3)

        item_4 = Item.objects.create()
        self.assertEqual(item_4.reusable_number, 3)
        self.assertEqual(Sequence.get_current_value('reusable_items'), 3)

        item_5 = Item.objects.create()
        self.assertEqual(item_5.reusable_number, 4)
        self.assertEqual(Sequence.get_current_value('reusable_items'), 4)

    def test_sequence_field_resolves_integrity_errors(self) -> None:
        item_1 = Item.objects.create()
        self.assertEqual(item_1.unique_number, 1)
        self.assertEqual(Sequence.get_current_value('unique_items'), 1)

        Sequence.objects.filter(key='unique_items').delete()
        self.assertEqual(Sequence.get_current_value('unique_items'), 0)

        item_2 = Item.objects.create()
        self.assertEqual(item_2.unique_number, 2)
        self.assertEqual(Sequence.get_current_value('unique_items'), 2)

        item_3 = Item.objects.create()
        self.assertEqual(item_3.unique_number, 3)
        self.assertEqual(Sequence.get_current_value('unique_items'), 3)

        Sequence.objects.filter(key='unique_items').update(value=1)
        self.assertEqual(Sequence.get_current_value('unique_items'), 1)

        item_4 = Item.objects.create()
        self.assertEqual(item_4.unique_number, 4)
        self.assertEqual(Sequence.get_current_value('unique_items'), 4)
