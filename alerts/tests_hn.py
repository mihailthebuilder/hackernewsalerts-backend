from django.test import TestCase
from datetime import datetime, timezone
from . import hn


class HnGetNewCommentReplies(TestCase):
    def test_return_empty_list_when_items_is_none(self):
        hn.get_new_comment_replies("dabs", datetime.now(timezone.utc))

    # def test_some_users(self):
    #     print(hn.get_new_comment_replies("", datetime.now(timezone.utc)))
    #     print(hn.get_new_post_comments("", datetime.now(timezone.utc)))
