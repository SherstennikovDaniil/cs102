import io
import os
import sys
import typing as tp
import unittest
import unittest.mock as mock

import __main__  # workaround for unpickling NaiveBayesClassifier
import responses
from bottle import HTTPResponse

# Since we can't just swap databases in-flight, we have to get creative. There is a fake_db.py in the top-level dir
# (top-level is used to avoid including that script into the tests package, which induced namespacing problems)
# So first we add the top-level directory to the import search path...
sys.path.append(f"{os.path.dirname(os.path.realpath(__file__))}/../")
# ...and then we swap out the package in globals() with the fake_db we can now import
sys.modules["naive_bayes.db"] = __import__("fake_db")
import fake_db  # we also need it here

# import structure here will be:
# this module imports naive_bayes.hackernews
# hackernews tries importing naive_bayes.db, instead imports fake_db from top-level dir due to module tampering
# accessing naive_bayes.db session from naive_bayes.hackernews actually gets a session to a mock in-memory database created in fake_db.py
import naive_bayes.hackernews as h_news
from boddle import boddle
from naive_bayes.bayes import NaiveBayesClassifier
from sqlalchemy.orm import close_all_sessions


class HackernewsTestCase(unittest.TestCase):
    def __init__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        __main__.NaiveBayesClassifier = NaiveBayesClassifier  # workaround
        # pickle serializes classes relative to main, because of that the unpickling fails if NaiveBayesClassifier is not in globals() for unittest.__main__
        # thus we inject the class object directly into __main__
        unittest.TestCase.__init__(self, *args, **kwargs)

    def setUp(self) -> None:
        fake_db.Base.metadata.create_all(bind=fake_db.engine)
        s = fake_db.session()
        extracts = [
            {
                "author": "blasrodri",
                "comments": 0,
                "points": 1,
                "title": "Oracle Cloud to Acquire Linux Kernel Technology eBPF",
                "url": "https://cilium.io/blog/2021/04/01/oracle-cloud-acquired-ebpf",
            },
            {
                "author": "adenozine",
                "comments": 0,
                "points": 1,
                "title": "Tell HN: Thanks for the Maturity",
                "url": "item?id=26660719",
            },
            {
                "author": "CapitalistCartr",
                "comments": 0,
                "points": 2,
                "title": "Poorer and minority older adults are suspicious of the US health care system",
                "url": "https://theconversation.com/poorer-and-minority-older-adults-are-suspicious-of-the-us-health-care-system-a-new-study-shows-why-156117",
            },
        ]
        for i in extracts:
            obj = fake_db.News(
                title=i["title"],
                author=i["author"],
                url=i["url"],
                comments=i["comments"],
                points=i["points"],
            )
            s.add(obj)
            s.commit()

    def test_add_label(self) -> None:
        with boddle(query={"id": "1", "label": "good"}):
            try:
                h_news.add_label()
            except HTTPResponse:
                pass  # ignore redirects
        s = fake_db.session()
        row = s.query(fake_db.News).filter(fake_db.News.id == 1).first()
        print(f"got row: ", row.title)
        label = row.label
        self.assertEqual(label, "good")

    @responses.activate  # type: ignore
    def test_update_news(self) -> tp.Any:
        with open(
            f"{os.path.dirname(os.path.realpath(__file__))}/mock_templates/example_new_extracts_response.html"
        ) as f:
            mock_response_text = f.read()
        responses.add(responses.GET, "https://news.ycombinator.com/newest", body=mock_response_text)
        with unittest.mock.patch("sys.stdout", new=io.StringIO()) as _:
            try:
                h_news.update_news()
            except HTTPResponse:
                pass  # ignore redirects
        s = fake_db.session()
        rows = s.query(fake_db.News).all()  # should be the last one
        self.assertGreater(len(rows), 30)

    def test_classify_news(self) -> None:
        try:
            h_news.classify_news()
        except HTTPResponse:
            pass  # ignore redirects
        s = fake_db.session()
        rows = s.query(fake_db.News).filter(fake_db.News.label is None).all()
        self.assertFalse(rows)

    def tearDown(self) -> None:
        s = fake_db.session()
        rows = s.query(fake_db.News).all()
        for row in rows:
            s.delete(row)
            s.commit()
        close_all_sessions()
        fake_db.Base.metadata.drop_all(bind=fake_db.engine)
