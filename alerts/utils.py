from datetime import datetime
from bs4 import BeautifulSoup
from django.core import signing


def format_date(input: datetime) -> str:
    return input.strftime("%H:%M %d-%m")


def html_to_str(input: str) -> str:
    return BeautifulSoup(input, "html.parser").get_text()


class UnsubscribeSigner:
    SALT = "unsubscribe-salt"

    def __init__(self):
        self.signer = signing.Signer(salt=self.SALT)

    def make_token(self, username: str) -> str:
        return self.signer.sign(username)

    def read_token(self, token: str) -> str:
        return self.signer.unsign(token)


class PostUnsubscribeSigner:
    SALT = "post-unsubscribe-salt"

    def make_token(self, username: str, post_id: str) -> str:
        return signing.dumps({"u": username, "p": post_id}, salt=self.SALT)

    def read_token(self, token: str) -> tuple[str, str]:
        data = signing.loads(token, salt=self.SALT)
        return data["u"], data["p"]
