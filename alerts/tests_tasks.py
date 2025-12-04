from . import tasks, models
from django.test import TestCase
from datetime import timedelta
import os
from django.utils.timezone import now


class HnGetNewCommentReplies(TestCase):
    def test_user(self):

        if os.environ["TEST_RUN_TASK"] == "1":
            user = models.User(
                hn_username=os.environ["TEST_HN_USERNAME"],
                email=os.environ["TEST_USER_EMAIL"],
                is_verified=True,
                last_checked=now() - timedelta(days=1),
            )

            tasks.process_user(user)
        else:
            print("Skipping test; set TEST_RUN_TASK=1 to run")
