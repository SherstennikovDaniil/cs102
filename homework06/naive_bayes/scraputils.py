import re
import typing as tp

import requests
from bs4 import BeautifulSoup


def extract_news(parser: BeautifulSoup) -> tp.List[tp.Dict[str, tp.Any]]:
    """ Extract news from a given web page """
    news_list: tp.List[tp.Dict[str, tp.Any]] = []

    authors: tp.List[str] = [i.text for i in parser.body.find_all("a", {"class": "hnuser"})]
    comments: tp.List[tp.Any] = [
        i for i in parser.body.find_all("a") if "item?id=" in i.attrs["href"]
    ]  # get link and assorted garbage
    comments = [
        i.text for i in comments if (re.match(r"\d+\scomment", i.text) or i.text == "discuss")
    ]  # get text
    comment_counts: tp.List[int] = [
        int(i[: i.find("\xa0")]) if not "discuss" in i else 0 for i in comments
    ]  # clean up
    points: tp.List[int] = [
        int(i.text[: i.text.find(" ")]) for i in parser.body.find_all("span", {"class": "score"})
    ]
    titles: tp.List[str] = [i.text for i in parser.body.find_all("a", {"class": "storylink"})]
    urls: tp.List[str] = [
        i.attrs["href"] for i in parser.body.find_all("a", {"class": "storylink"})
    ]

    for i, _ in enumerate(authors):
        extract = {
            "author": authors[i],
            "comments": comment_counts[i],
            "points": points[i],
            "title": titles[i],
            "url": urls[i],
        }
        news_list.append(extract)

    return news_list


def extract_next_page(parser: BeautifulSoup) -> str:
    """ Extract next page URL """
    morelink: str = parser.body.find("a", {"class": "morelink"}).attrs["href"]
    return morelink


def get_news(url: str, n_pages: int = 1) -> tp.List[tp.Dict[str, tp.Any]]:
    """ Collect news from a given web page """
    news: tp.List[tp.Dict[str, tp.Any]] = []
    while n_pages:
        print("Collecting data from page: {}".format(url))
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        news_list = extract_news(soup)
        next_page = extract_next_page(soup)
        url = "https://news.ycombinator.com/" + next_page
        news.extend(news_list)
        n_pages -= 1
    return news
