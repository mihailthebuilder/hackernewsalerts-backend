from ninja import NinjaAPI, Schema
from django import http
from pydantic import EmailStr
from http import HTTPStatus
import logging
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.html import escape

from . import mail, models, utils
from django.core import signing
import os

api = NinjaAPI()
signer = signing.Signer(sep="$")


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
    ui_url = os.environ["UI_URL"]
    verification_link = f"{ui_url}?verificationCode={verification_code}"
    content = f"Thank you for signing up to hackernewsalerts.com! Please verify your email address by clicking the link below: {verification_link}"

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


@api.get("/unsubscribe/")
def unsubscribe_preview(request, token: str):
    try:
        utils.UnsubscribeSigner().read_token(token)  # validate only
    except signing.BadSignature:
        return HttpResponse("Invalid unsubscribe link.", status=400)

    safe_token = escape(token)

    return HttpResponse(
        f"""
        <html>
            <body style="font-family: sans-serif; padding: 40px;">
                <h2>Confirm Unsubscribe?</h2>

                <form method="post" action="/api/unsubscribe/confirm/?token={safe_token}">
                    <button type="submit">
                        Yes, unsubscribe me
                    </button>
                </form>
            </body>
        </html>
    """
    )


@csrf_exempt
@api.post("/unsubscribe/confirm/")
def unsubscribe_confirm(request, token: str):
    try:
        username = utils.UnsubscribeSigner().read_token(token)
    except signing.BadSignature:
        return HttpResponse("Invalid unsubscribe link.", status=400)

    user = get_object_or_404(models.User, hn_username=username)
    user.delete()

    logging.info(f"User {username} unsubscribed.")
    return HttpResponse("You have been permanently unsubscribed.")
