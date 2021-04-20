import os
import pathlib
import pickle
import typing as tp

import naive_bayes.stemmer
from bottle import redirect, request, route, run, template
from naive_bayes.bayes import NaiveBayesClassifier
from naive_bayes.db import News, session
from naive_bayes.scraputils import get_news


@route("/")  # type: ignore
def index() -> tp.Any:
    redirect("/news")


@route("/news")  # type: ignore
def news_list() -> tp.Any:
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("templates/news_template", rows=rows)


@route("/add_label/")  # type: ignore
def add_label() -> tp.Any:
    s = session()
    entry = s.query(News).filter(News.id == request.query["id"]).first()  # only one such row exists
    entry.label = request.query["label"]
    s.commit()
    redirect("/news")


@route("/update")  # type: ignore
def update_news() -> tp.Any:
    new_arrivals = get_news("https://news.ycombinator.com/newest")
    s = session()
    marker = s.query(News).first()  # Isaac Clarke's nightmare
    batch_size: int = 30  # there are 30 news entries per page. Just trust me on that.
    for i, e in enumerate(new_arrivals):
        if e["title"] == marker.title and e["author"] == marker.author:
            batch_size = i
    new_arrivals = new_arrivals[:batch_size]
    for entry in new_arrivals:
        obj = News(
            title=entry["title"],
            author=entry["author"],
            url=entry["url"],
            comments=entry["comments"],
            points=entry["points"],
        )
        s.add(obj)
        s.commit()
    redirect("/news")


@route("/classify")  # type: ignore
def classify_news() -> tp.Any:
    s = session()
    unclassified: tp.List[tp.Tuple[int, str]] = [
        (i.id, naive_bayes.stemmer.clear(i.title))
        for i in s.query(News).filter(News.label == None).all()
    ]
    X: tp.List[str] = [i[1] for i in unclassified]
    if not pathlib.Path(
        f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle"
    ).is_file():
        raise ValueError(
            "Classifier is untrained! Please mark enough news to adequately train the model and run bayes.py to save it."
        )
    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle", "rb"
    ) as model_file:
        model = naive_bayes.bayes.NaiveBayesClassifier(alpha=0.1)
        model = pickle.load(model_file)
    labels = model.predict(X)
    for i, e in enumerate(unclassified):
        extract = s.query(News).filter(News.id == e[0]).first()  # only one such news extract exists
        extract.label = labels[i]
        s.commit()
    rows = s.query(News).filter(News.label != None).order_by(News.label).all()
    return template("templates/classified_template", rows=rows)


if __name__ == "__main__":
    run(host="localhost", port=8080)
