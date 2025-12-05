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
