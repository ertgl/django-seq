from concurrent.futures import (
    Future,
    ThreadPoolExecutor,
)
from contextlib import ExitStack
import multiprocessing
from typing import List

from django import db
from django.db import transaction
from django.test import TransactionTestCase

from django_seq.utils import get_sequence_model


Sequence = get_sequence_model()


class SequenceTransactionTestCase(TransactionTestCase):

    def test_increase_value(self) -> None:

        def _increase_value() -> int:
            value: int
            with ExitStack() as stack, transaction.atomic():
                stack.callback(db.close_old_connections)
                value = Sequence.get_next_value('repositories.1.issues')
            return value

        workers_count = min(max(multiprocessing.cpu_count(), 8), 64)

        futures: List[Future[int]] = []

        with ThreadPoolExecutor(max_workers=workers_count) as executor:
            for _ in range(workers_count):
                future = executor.submit(_increase_value)
                futures.append(future)

        results: List[int] = []

        for future in futures:
            results.append(future.result())

        self.assertEqual(
            Sequence.get_current_value('repositories.1.issues'),
            workers_count,
        )

        for i in range(workers_count):
            self.assertIn(i + 1, results)

        self.assertEqual(
            Sequence.get_current_value('repositories.2.issues'),
            0,
        )
