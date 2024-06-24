from .models import User
from .hn import get_new_comment_replies, get_new_post_comments
from django.utils import timezone
import os


def send_alerts():
    try:
        users = User.objects.filter(is_verified=True)
        for user in users:
            post_comments = get_new_post_comments(
                user.hn_username, user.last_checked
            ).items
            comment_replies = get_new_comment_replies(
                user.hn_username, user.last_checked
            )
            now = timezone.now()

            if len(post_comments) + len(comment_replies) > 0:
                content = f"Hi {user.email}. You have {len(post_comments)} new comments to your posts, and {len(comment_replies)} replies to your comments"
                send_email(user.email, content)

            user.last_checked = now
            user.save()
    except Exception as e:
        content = "Error in alerts"
        send_email(os.environ["ERROR_ALERTS_TO"], content)
        raise e


def send_email(to: str, content: str):
    print(content)
