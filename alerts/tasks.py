from . import models, hn, mail
from django.contrib.auth.models import User

from django.utils import timezone
import logging


def send_alerts():
    try:
        users = models.User.objects.filter(is_verified=True)
        for user in users:
            post_comments = hn.get_new_post_comments(
                user.hn_username, user.last_checked
            ).items
            comment_replies = hn.get_new_comment_replies(
                user.hn_username, user.last_checked
            )
            now = timezone.now()

            if len(post_comments) + len(comment_replies) > 0:
                content = f"Hi {user.email}. You have {len(post_comments)} new comments to your posts, and {len(comment_replies)} replies to your comments"
                subject = "Hacker News alerts"
                mail.send_mail(user.email, subject, content)

            user.last_checked = now
            user.save()
    except Exception as e:
        content = f"Error in alerts: {e}"
        logging.error(content)

        admin = User.objects.get(is_superuser=True)
        subject = "hackernewsalerts.com tasks error"
        mail.send_mail(admin.email, subject, content)
