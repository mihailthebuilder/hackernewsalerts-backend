from . import models, hn, mail, utils
from django.contrib.auth import models as admin_models
import traceback

from django.utils import timezone
import logging


def check_for_alerts():
    users = models.User.objects.filter(is_verified=True)
    error_count = 0

    for user in users:
        try:
            process_user(user)
        except Exception as e:
            e.add_note(f"error processing user: {user.hn_username}")
            logging.error(traceback.format_exc())
            error_count += 1

    if error_count > 0:
        admin = admin_models.User.objects.get(is_superuser=True)
        subject = "hackernewsalerts.com tasks error"
        mail.send_mail(admin.email, subject, f"{error_count} errors encountered")


def process_user(user: models.User):
    post_comments = hn.get_new_post_comments(user.hn_username, user.last_checked).items
    comment_replies = hn.get_new_comment_replies(user.hn_username, user.last_checked)
    now = timezone.now()

    len_post_comments = len(post_comments)
    len_comment_replies = len(comment_replies)

    if len_post_comments + len_comment_replies > 0:
        print(
            f"Preparing to send email to {user.hn_username}; {len_post_comments} post comments; {len_comment_replies} comment replies"
        )
        content = ""
        subject = ""

        if len_post_comments > 0:
            comment_word = "comment" if len_post_comments == 1 else "comments"

            subject = f"{len_post_comments} {comment_word}"

            content = (
                content
                + f"You have {len_post_comments} new {comment_word} to your posts:\n\n"
            )

            for comment in post_comments:
                date = utils.format_date(comment.date_published)

                content = (
                    content + f"{date} - {comment.author.name} - {comment.external_url}"
                )
                content = content + utils.html_to_str(comment.content_html) + "\n"

        if len_comment_replies > 0:
            reply_word = "reply" if len_comment_replies == 1 else "replies"

            if len_post_comments > 0:
                subject += " / "

            subject += f"{len_comment_replies} {reply_word}"

            content = (
                content
                + f"You have {len_comment_replies} new {reply_word} to your comments:\n\n"
            )

            for reply in comment_replies:
                date = utils.format_date(reply.date_published)

                content = (
                    content + f"{date} - {reply.author.name} - {reply.external_url}"
                )
                content = content + utils.html_to_str(reply.content_html) + "\n"

        subject += f" - {utils.format_date(now)}"
        content = (
            content
            + "\n\n"
            + "Want to unsubscribe? Just reply to this email to let us know."
        )

        mail.send_mail(user.email, subject, content)

    user.last_checked = now
    user.save()
