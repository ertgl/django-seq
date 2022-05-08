from django.test import TestCase
from issues.models import (
    Issue,
    Repository,
)


class IssueTestCase(TestCase):

    def test_sequence_field(self) -> None:

        repositories_count = 10
        repositories = [
            Repository.objects.create()
            for _ in range(repositories_count)
        ]

        issues_count = 10
        for repository_idx in range(repositories_count):
            for issue_idx in range(issues_count):
                issue = Issue.objects.create(
                    repository=repositories[repository_idx],
                )
                self.assertEqual(issue.index, issue_idx + 1)
