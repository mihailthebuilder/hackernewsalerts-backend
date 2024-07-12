import requests
from datetime import UTC, datetime, timedelta
from pydantic import BaseModel

from urllib.parse import urlparse, parse_qs


class ItemAuthor(BaseModel):
    name: str
    url: str


class Item(BaseModel):
    id: str
    title: str
    content_html: str
    url: str
    external_url: str
    date_published: datetime
    author: ItemAuthor


def get_new_comment_replies(
    username: str, oldest_date_considered: datetime
) -> list[Item]:
    replies_url = f"https://hnrss.org/replies.jsonfeed?id={username}"
    replies_response_json = requests.get(replies_url).json()["items"]

    if replies_response_json == None:
        return []

    replies = [Item(**reply) for reply in replies_response_json]
    filtered_replies = [
        reply
        for reply in replies
        if reply.author.name != username
        and reply.date_published > oldest_date_considered
    ]

    return filtered_replies


class GetNewPostCommentsResult(BaseModel):
    user_found: bool
    items: list[Item]


def get_new_post_comments(
    username: str, oldest_date_considered: datetime
) -> GetNewPostCommentsResult:

    posts_url = f"https://hnrss.org/submitted.jsonfeed?id={username}"
    posts_response_json = requests.get(posts_url).json()["items"]

    result = GetNewPostCommentsResult(user_found=False, items=[])

    if posts_response_json == None:
        return result

    result.user_found = True

    posts = [Item(**post) for post in posts_response_json]
    oldest_active_post_date = (datetime.now() - timedelta(days=14)).replace(tzinfo=UTC)
    posts_open_for_discussion = [
        post for post in posts if post.date_published > oldest_active_post_date
    ]

    for post in posts_open_for_discussion:
        parsed_url = urlparse(post.external_url)
        query_params = parse_qs(parsed_url.query)
        post_id = query_params["id"][0]

        comments_url = f"https://hnrss.org/item.jsonfeed?id={post_id}"
        comments_response_json = requests.get(comments_url).json()["items"]

        if comments_response_json is None:
            continue

        comments = [Item(**comment) for comment in comments_response_json]

        filtered_comments = [
            comment
            for comment in comments
            if comment.author.name != username
            and comment.date_published > oldest_date_considered
        ]

        result.items = result.items + filtered_comments

    return result
