from .models import User
from .hn import get_new_comment_replies, get_new_post_comments
from django.core.mail import send_mail


def send_alerts():
    users = User.objects.filter(is_verified=True)
    for user in users:
        post_comments = get_new_post_comments(user.hn_username, user.last_checked).items
        comment_replies = get_new_comment_replies(user.hn_username, user.last_checked)

        if len(post_comments) + len(comment_replies) > 0:
            send_mail(
                "New comments/replies on HN",
                f"You have {len(post_comments)} new comments to your posts, and {len(comment_replies)} replies to your comments",
                "testing@gmail.com",
                [user.email],
            )


def handle_send_alerts_result(task):
    print(task.result)
