from ninja import NinjaAPI, Schema
from django import http
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC
from pydantic import EmailStr
from http import HTTPStatus
import logging

from . import mail, hn, models
from django.core import signing
import os

api = NinjaAPI()
signer = signing.Signer(sep="$")


class RenderedItem(Schema):
    url: str
    text: str
    date: str


@api.get("/alerts/{username}")
def get_alerts(request, username: str):
    timeframe = timedelta(days=1)
    oldest_date_considered = (datetime.now() - timeframe).replace(tzinfo=UTC)

    result = hn.get_new_post_comments(username, oldest_date_considered)
    if not result.user_found:
        return http.HttpResponseNotFound("HN username not found")

    comment_replies = hn.get_new_comment_replies(username, oldest_date_considered)

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
    existing_user = models.User.objects.filter(hn_username=payload.hn_username).first()
    if existing_user is not None:
        logging.info(f"HN username {payload.hn_username} already exists")
        return http.HttpResponseBadRequest("alert already set up for HN username")

    user = models.User.objects.create(**payload.dict())

    send_verification_email(user)

    user.save()

    return http.HttpResponse(status=HTTPStatus.CREATED)


def send_verification_email(user: models.User):
    verification_code = signer.sign(user.hn_username)
    verification_link = f"{os.environ["UI_URL"]}?verificationCode={verification_code}"
    content = f"Thank you for singing up to hackernewsalerts.com! Please verify your email address by clicking the link below: {verification_link}"

    subject = "Verify your email for hackernewsalerts.com"
    mail.send_mail(to=user.email, subject=subject, content=content)

@api.post("/verify/{code}")
def verify_email(request, code: str):
    try:
        hn_username = signer.unsign(code)
    except signing.BadSignature:
        return http.HttpResponseBadRequest("invalid code")
    
    try:
        user = models.User.objects.get(hn_username=hn_username)
    except models.User.DoesNotExist:
        return http.HttpResponseNotFound()
    
    user.is_verified = True
    user.save()

    return http.HttpResponse(status=HTTPStatus.OK)
