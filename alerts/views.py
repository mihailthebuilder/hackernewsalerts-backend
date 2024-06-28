from ninja import NinjaAPI
from ninja import Schema
from django import http
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
from pydantic import EmailStr
from http import HTTPStatus
import logging

from .models import User
from .mail import send_mail
from .hn import get_new_comment_replies, get_new_post_comments
from django.core.signing import Signer
import os

api = NinjaAPI()


class RenderedItem(Schema):
    url: str
    text: str
    date: str


@api.get("/alerts/users/{username}")
def get_alerts(request, username: str):
    timeframe = timedelta(days=1)
    oldest_date_considered = (datetime.now() - timeframe).replace(tzinfo=UTC)

    result = get_new_post_comments(username, oldest_date_considered)
    if not result.user_found:
        return http.HttpResponseNotFound("HN username not found")

    comment_replies = get_new_comment_replies(username, oldest_date_considered)

    return {
        "post_comments": [
            RenderedItem(
                url=item.external_url,
                text=BeautifulSoup(item.content_html, "html.parser").get_text(),
                date=item.date_published.strftime("%H:%M %d-%m"),
            )
            for item in result.items
        ],
        "comment_replies": [
            RenderedItem(
                url=item.external_url,
                text=BeautifulSoup(item.content_html, "html.parser").get_text(),
                date=item.date_published.strftime("%H:%M %d-%m"),
            )
            for item in comment_replies
        ],
    }


class UserCreate(Schema):
    hn_username: str
    email: EmailStr


@api.post("/signup")
def create_alert(request, payload: UserCreate):
    existing_user = User.objects.filter(hn_username=payload.hn_username).first()
    if existing_user is not None:
        logging.info(f"HN username {payload.hn_username} already exists")
        return http.HttpResponseBadRequest("alert already set up for HN username")

    user = User.objects.create(**payload.dict())

    send_verification_email(user)

    user.save()

    return http.HttpResponse(status=HTTPStatus.CREATED)

@api.post("")


def send_verification_email(user: User):
    to = user.email

    signer = Signer()
    verification_code = signer.sign(to)
    verification_link = f"{os.environ["WEB_URL"]}/verify/{verification_code}"
    content = f"Thank you for singing up to hackernewsalerts.com! Please verify your email address by clicking the link below: {verification_link}"

    subject = "Verify your email for hackernewsalerts.com"
    send_mail(to=to, subject=subject, content=content)
