import itertools
import math
import operator
import os
import pathlib
import pickle
import typing as tp
from collections import Counter, defaultdict
from copy import deepcopy

import naive_bayes.stemmer
from naive_bayes.db import News, session


class NaiveBayesClassifier:
    def __init__(self, alpha: float) -> None:
        if not 0.0 < alpha <= 1.0:
            raise ValueError("Smoothing parameter must be between 0.0 and 1.0")
        self.priors: tp.Counter[str] = Counter()  # prior probabilities of classes
        self.alpha: float = alpha  # smoothing parameter
        self.unique_words: tp.List[str] = []
        self.words_per_class: tp.DefaultDict[str, tp.DefaultDict[str, float]] = defaultdict(
            defaultdict
        )
        self.class_lengths: tp.DefaultDict[str, float] = defaultdict(float)
        self.word_probs: tp.DefaultDict[str, tp.DefaultDict[str, float]] = defaultdict(defaultdict)

    def fit(self, X: tp.List[str], y: tp.List[str]) -> None:
        """ Fit Naive Bayes classifier according to X, y. """
        if not X or not y or not len(X) == len(y):
            raise ValueError("The training set is either unmarked or empty.")
        self.priors = Counter(y)
        for e in self.priors:
            self.priors[e] /= len(y)  # type: ignore
        unique_words_unflat = [i.split(" ") for i in X]
        self.unique_words = list(itertools.chain.from_iterable(unique_words_unflat))
        self.unique_words = sorted(list(set(self.unique_words)))
        self.words_per_class = defaultdict(defaultdict)
        self.class_lengths = defaultdict(float)
        for i, string in enumerate(X):
            words: tp.List[str] = string.split(" ")
            c = y[i]
            self.class_lengths[c] += len(words)
            for word in words:
                if not word in self.words_per_class.keys():
                    self.words_per_class[word] = defaultdict(
                        float,
                        {
                            key: value
                            for (key, value) in zip(list(set(y)), [0 for _ in list(set(y))])
                        },
                    )
                    # very hack-y way of assigning 0 encounters to each class in possible classes
                self.words_per_class[word][c] += 1
        self.word_probs = deepcopy(self.words_per_class)
        for word, value in self.word_probs.items():
            for c, _ in value.items():
                self.word_probs[word][c] = (self.word_probs[word][c] + self.alpha) / (
                    self.class_lengths[c] + self.alpha * len(self.unique_words)
                )

    def predict(self, X: tp.List[str]) -> tp.List[str]:
        """ Perform classification on an array of test vectors X. """
        if (
            not self.priors
            or not self.unique_words
            or not self.words_per_class
            or not self.class_lengths
            or not self.word_probs
        ):
            raise ValueError("The model is untrained")
        labels: tp.List[str] = []
        for document in X:
            words: tp.List[str] = document.split(" ")
            probabilities: tp.DefaultDict[str, float] = defaultdict(float)
            for c in self.class_lengths.keys():
                word_probs = []
                for word in words:
                    if word in self.unique_words:
                        word_probs.append(math.log(self.word_probs[word][c]))
                word_probs_sum = sum(word_probs)
                probabilities[c] = math.log(self.priors[c]) + word_probs_sum
            predicted_label = max(probabilities.items(), key=operator.itemgetter(1))[0]
            # see https://stackoverflow.com/questions/268272/getting-key-with-maximum-value-in-dictionary
            labels.append(predicted_label)
        return labels

    def score(self, X_test: tp.List[str], y_test: tp.List[str]) -> float:
        """ Returns the mean accuracy on the given test data and labels. """
        predicted: tp.List[str] = self.predict(X_test)
        class_accuracies = defaultdict(float)
        for c in list(set(y_test)):
            if y_test.count(c):
                true_positives: float = float(
                    sum([1 for i, e in enumerate(predicted) if e == c and y_test[i] == c])
                )
                false_negatives: float = float(
                    sum([1 for i, e in enumerate(predicted) if e != c and y_test[i] == c])
                )
                class_accuracies[c] = true_positives / (true_positives + false_negatives)
        score: float = sum([i for i in class_accuracies.values()]) / len(list(set(y_test)))
        return score


if __name__ == "__main__":
    if not pathlib.Path(
        f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle"
    ).is_file():
        print("No model detected. Creating new model...")
        model = NaiveBayesClassifier(alpha=0.1)
        print("Extracting marked news from database...")
        s = session()
        classified = [(i.title, i.label) for i in s.query(News).filter(News.label != None).all()]
        X_train, y_train = [], []
        for label, extract in classified:
            X_train.append(label)
            y_train.append(extract)
        X_train = [naive_bayes.stemmer.clear(x).lower() for x in X_train]
        print(f"Extracted {len(X_train)} marked news")
        print("Training model...")
        model.fit(X_train, y_train)
        print("Model retrained. Saving...")
        with open(
            f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle", "wb"
        ) as model_file:
            pickle.dump(model, model_file)
        print("Successfully saved model!")
    else:
        print(f"Model already exists.")
