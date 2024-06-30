from . import models, hn, mail, utils
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
                content = ""

                if len(post_comments) > 0:
                    content = (
                        content
                        + f"You have {len(post_comments)} new comments to your posts:\n\n"
                    )

                    for comment in post_comments:
                        date = utils.format_date(comment.date_published)
                        url = f"https://news.ycombinator.com/item?id={comment.id}"

                        content = content + f"{date} - {comment.author} - {url}\n"
                        content = (
                            content + utils.html_to_str(comment.content_html) + "\n\n"
                        )

                    content += "\n\n\n"

                if len(comment_replies) > 0:
                    content = (
                        content
                        + f"You have {len(comment_replies)} new replies to your comments:\n\n"
                    )

                    for reply in comment_replies:
                        date = utils.format_date(reply.date_published)
                        url = f"https://news.ycombinator.com/item?id={reply.id}"

                        content = content + f"{date} - {reply.author} - {url}\n"
                        content = (
                            content + utils.html_to_str(reply.content_html) + "\n\n"
                        )

                subject = "New comments/replies on Hacker News"
                mail.send_mail(user.email, subject, content)

            user.last_checked = now
            user.save()

    except Exception as e:
        content = f"Error in alerts: {e}"
        logging.error(content)

        admin = User.objects.get(is_superuser=True)
        subject = "hackernewsalerts.com tasks error"
        mail.send_mail(admin.email, subject, content)
