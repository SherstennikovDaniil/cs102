import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []
    authors = [x.text for x in parser.body.findall("a", {"class": "hnuser"})]
    comments = [x for x in parser.body.findall("a") if "item&id=" in x.attrs["href"]]
    return news_list, authors


def extract_next_page(parser):
    """ Extract next page URL """
    # PUT YOUR CODE HERE


def get_news(url, n_pages=1):
    """ Collect news from a given web page """
    news = []
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
