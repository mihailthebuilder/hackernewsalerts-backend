from . import tasks, models
from django.test import TestCase
from datetime import timedelta
from django.utils.timezone import now


class HnGetNewCommentReplies(TestCase):
    def test_user(self):
        user = models.User(
            hn_username="",
            email="test@test.com",
            is_verified=True,
            last_checked=now() - timedelta(days=1),
        )
        # tasks.process_user(user)
