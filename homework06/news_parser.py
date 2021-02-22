import requests as r


def get_news(n_pages: int):
    req = r.get("https://hacker-news.firebaseio.com/v0/newstories.json?print=pretty")
    id_list = list(req.json())
    posts = []
    for id in id_list[: n_pages * 30]:
        req = r.get(
            f"https://hacker-news.firebaseio.com/v0/item/{id}.json?print=pretty"
        )
        posts.append(req.json())
    news = []
    for post in posts:
        post_reformat = {
            "author": post.get("by"),
            "comments": post.get("descendants"),
            "points": post.get("score"),
            "title": post.get("title"),
            "url": post.get("url"),
        }
        news.append(post_reformat)
    return news


if __name__ == "__main__":
    lol = get_news(1)
    for l in lol:
        print(l)
