from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.core import signing
from django.test import TestCase
from django.utils.timezone import now

from . import hn, models, utils


def _feed_item(item_id: str, *, author: str, external_url: str, published: datetime):
    return {
        "id": item_id,
        "title": f"title {item_id}",
        "content_html": f"<p>body {item_id}</p>",
        "url": f"https://news.ycombinator.com/item?id={item_id}",
        "external_url": external_url,
        "date_published": published.isoformat(),
        "author": {
            "name": author,
            "url": f"https://news.ycombinator.com/user?id={author}",
        },
    }


class PostUnsubscribeSignerTest(TestCase):
    def test_round_trip(self):
        token = utils.PostUnsubscribeSigner().make_token("alice", "12345")
        username, post_id = utils.PostUnsubscribeSigner().read_token(token)
        self.assertEqual(username, "alice")
        self.assertEqual(post_id, "12345")

    def test_bad_signature_on_mangled_token(self):
        token = utils.PostUnsubscribeSigner().make_token("alice", "12345")
        with self.assertRaises(signing.BadSignature):
            utils.PostUnsubscribeSigner().read_token(token + "tampered")


class GetNewPostCommentsMutingTest(TestCase):
    def _patched_get(self, post_id="123"):
        recent = now()
        post_url = f"https://news.ycombinator.com/item?id={post_id}"

        def fake_get(url, *args, **kwargs):
            class FakeResponse:
                def __init__(self, payload):
                    self._payload = payload

                def json(self):
                    return {"items": self._payload}

            if "submitted.jsonfeed" in url:
                return FakeResponse(
                    [
                        _feed_item(
                            post_id,
                            author="me",
                            external_url=post_url,
                            published=recent,
                        )
                    ]
                )
            # item.jsonfeed (comments)
            return FakeResponse(
                [
                    _feed_item(
                        "999",
                        author="someone_else",
                        external_url="https://news.ycombinator.com/item?id=999",
                        published=recent,
                    )
                ]
            )

        return fake_get

    def test_includes_post_when_not_muted(self):
        oldest = now() - timedelta(days=1)
        with patch("alerts.hn.requests.get", side_effect=self._patched_get()):
            result = hn.get_new_post_comments("me", oldest)
        self.assertEqual(len(result.posts), 1)
        self.assertEqual(result.posts[0].post_id, "123")
        self.assertEqual(len(result.posts[0].comments), 1)

    def test_skips_muted_post(self):
        oldest = now() - timedelta(days=1)
        with patch("alerts.hn.requests.get", side_effect=self._patched_get()):
            result = hn.get_new_post_comments("me", oldest, muted_post_ids={"123"})
        self.assertEqual(result.posts, [])


class UnsubscribePostConfirmViewTest(TestCase):
    def setUp(self):
        self.user = models.User.objects.create(
            hn_username="bob", email="bob@example.com", is_verified=True
        )

    def test_confirm_creates_muted_post_and_is_idempotent(self):
        token = utils.PostUnsubscribeSigner().make_token("bob", "777")
        url = f"/api/unsubscribe/post/confirm/?token={token}"

        first = self.client.post(url)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(
            models.MutedPost.objects.filter(user=self.user, post_id="777").count(), 1
        )

        second = self.client.post(url)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(
            models.MutedPost.objects.filter(user=self.user, post_id="777").count(), 1
        )

    def test_preview_rejects_bad_token(self):
        response = self.client.get("/api/unsubscribe/post/?token=not-a-real-token")
        self.assertEqual(response.status_code, 400)
