from django.contrib.auth.models import User
from django.test import TransactionTestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS

from bookmarks.tests.helpers import BookmarkFactoryMixin


class BookmarkIndexViewPerformanceTestCase(TransactionTestCase, BookmarkFactoryMixin):

    def setUp(self) -> None:
        user = self.get_or_create_test_user()
        self.client.force_login(user)

    def get_connection(self):
        return connections[DEFAULT_DB_ALIAS]

    def test_should_not_increase_number_of_queries_per_bookmark(self):
        # create initial bookmarks
        num_initial_bookmarks = 10
        for index in range(num_initial_bookmarks):
            self.setup_bookmark(user=self.user)

        # capture number of queries
        context = CaptureQueriesContext(self.get_connection())
        with context:
            response = self.client.get(reverse('bookmarks:index'))
            self.assertContains(response, '<li ld-bookmark-item>', num_initial_bookmarks)

        number_of_queries = context.final_queries

        # add more bookmarks
        num_additional_bookmarks = 10
        for index in range(num_additional_bookmarks):
            self.setup_bookmark(user=self.user)

        # assert num queries doesn't increase
        with self.assertNumQueries(number_of_queries):
            response = self.client.get(reverse('bookmarks:index'))
            self.assertContains(response, '<li ld-bookmark-item>', num_initial_bookmarks + num_additional_bookmarks)
