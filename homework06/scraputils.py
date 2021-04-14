import requests
from bs4 import BeautifulSoup


def extract_news(parser):
    """ Extract news from a given web page """
    news_list = []
    body = parser.findAll('table', {'class': 'itemlist'})[0]
    tr = body.findChildren('tr')
    del tr[2::3]
    fathers = []
    news_list = []
    for x in range(0, len(tr), 2):
        values = tr[x: 2 + x]
        fathers.append(values)
    for father in fathers[:-1]:
        author = father[1].findChildren('a', {'class': 'hnuser'})[0].text
        comment = father[1].findChildren('td', {'class': 'subtext'})[0].findChildren('a')[-1].text
        if comment == 'discuss':
            comment = 0
        else:
            comment = int(comment[:-8])
        likes = father[1].findChildren('td', {'class': 'subtext'})[0].findChildren('span', {'class': 'score'})[0].text
        likes = int(likes.split(' ')[0])
        title = father[0].findChildren('a', {'class': 'storylink'})[0].text
        mur = father[0].findChildren('a', {'class': 'storylink'})[0]
        url = mur.get('href')
        news_list.append({
            'author': author,
            'comments': comment,
            'points': likes,
            'title': title,
            'url': url
        })
    return news_list


def extract_next_page(parser):
    """ Extract next page URL """
    return parser.find('a', {'class': 'morelink'}).get('href')


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
