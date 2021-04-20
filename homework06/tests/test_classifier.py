import csv
import os
import unittest

import naive_bayes.bayes as bayes
import naive_bayes.stemmer as stemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


class ClassifierTestCase(unittest.TestCase):
    def test_classifier_accuracy(self) -> None:
        with open(
            f"{os.path.dirname(os.path.realpath(__file__))}/../data/SMSSpamCollection"
        ) as f:  # fix for unknown error in unittests
            data = list(csv.reader(f, delimiter="\t"))
        X, y = [], []
        for target, msg in data:
            X.append(msg)
            y.append(target)
        X = [stemmer.clear(x).lower() for x in X]
        X_train, y_train, X_test, y_test = X[:3900], y[:3900], X[3900:], y[3900:]
        model = bayes.NaiveBayesClassifier(0.1)
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        print(f"Self-implemented classifier score: {score}")
        sk_model = Pipeline(
            [
                ("vectorizer", TfidfVectorizer()),
                ("classifier", MultinomialNB(alpha=0.05)),
            ]
        )
        sk_model.fit(X_train, y_train)
        print(f"sklearn MultinomialNB score: {sk_model.score(X_test, y_test)}")
