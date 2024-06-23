from django.urls import path
from ninja import NinjaAPI
from ninja import Schema

from bs4 import BeautifulSoup
from datetime import datetime, timedelta, UTC

from .hn import get_new_comment_replies, get_new_post_comments

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
    # if not result.user_found:
    #     raise HTTPException(status_code=404, detail="HN username not found")

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


urlpatterns = [
    path("", api.urls),
]
