from datetime import datetime
from bs4 import BeautifulSoup


def format_date(input: datetime) -> str:
    return input.strftime("%H:%M %d-%m")


def html_to_str(input: str) -> str:
    return BeautifulSoup(input, "html.parser").get_text()
