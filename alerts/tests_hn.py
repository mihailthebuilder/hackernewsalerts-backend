from django.test import TestCase
from datetime import datetime
from . import hn


class HnGetNewCommentReplies(TestCase):
    def test_return_empty_list_when_items_is_none(self):
        hn.get_new_comment_replies("dabs", datetime.now())
