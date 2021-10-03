import argparse
import datetime
import os
import pathlib
import pickle
import random
import shutil
import typing as tp

import naive_bayes.bayes as bayes
import naive_bayes.stemmer
import tqdm
from naive_bayes.bayes import NaiveBayesClassifier
from naive_bayes.db import News, session

VERBOSITY_LEVEL: int = 0


def verbose_print(content: str, level: int) -> None:
    if level <= VERBOSITY_LEVEL:
        tqdm.tqdm.write(content)


def clean_db() -> None:
    verbose_print("Cleaning database from labels", 3)
    s = session()
    verbose_print("Acquired session lock", 4)
    rows = s.query(News).all()
    verbose_print("Got news from database", 4)
    verbose_print(f"Length of data: {len(rows)}", 4)
    for i in tqdm.tqdm(range(len(rows)), desc="Clearing database"):
        extract = (
            s.query(News).filter(News.id == i + 1).first()
        )  # id is unique and enumerated from 1
        verbose_print(f"Found extract {extract.title}", 4)
        extract.label = None
        verbose_print("Set label to None", 4)
        s.commit()
        verbose_print("Committed to database", 4)
    verbose_print("Finished clearing labels", 3)


def randomize(marker: int) -> None:
    verbose_print(f"Randomizing first {marker} labels", 2)
    s = session()
    verbose_print("Acquired session lock", 4)
    rows = s.query(News).all()
    verbose_print("Got news from database", 4)
    verbose_print(f"Length of data: {len(rows)}", 4)
    for i in tqdm.tqdm(range(marker), desc="Writing random labels"):
        extract = (
            s.query(News).filter(News.id == i + 1).first()
        )  # id is unique and enumerated from 1
        verbose_print(f"Found extract {extract.title}", 4)
        extract.label = random.choice(["good", "maybe", "never"])
        verbose_print(f"Set label to {extract.label}", 4)
        s.commit()
        verbose_print("Committed to database", 4)
    verbose_print("Finished randomizing labels", 3)


def clean_model(alpha: float) -> None:
    verbose_print("Clearing model and retraining classifier", 3)
    pathlib.Path(f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle").unlink(
        missing_ok=True
    )
    model = bayes.NaiveBayesClassifier(alpha=alpha)
    verbose_print("extracting marked news from database...", 3)
    s = session()
    verbose_print("Acquired session lock", 4)
    classified = [(i.title, i.label) for i in s.query(News).filter(News.label != None).all()]
    verbose_print("Got labeled news from database", 4)
    verbose_print(f"Length of data: {len(classified)}", 4)
    X_train, y_train = [], []
    for label, extract in classified:
        X_train.append(label)
        y_train.append(extract)
    verbose_print("Moved data to X and y", 4)
    X_train = [naive_bayes.stemmer.clear(x).lower() for x in X_train]
    verbose_print("Training model...", 3)
    model.fit(X_train, y_train)
    verbose_print("Model retrained. Saving...", 3)
    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle", "wb"
    ) as model_file:
        pickle.dump(model, model_file)
    verbose_print("Successfully saved model!", 4)


def fill_database(alpha: float) -> NaiveBayesClassifier:
    verbose_print("Predicting labels to fill database", 3)
    s = session()
    verbose_print("Acquired session lock", 4)
    unclassified: tp.List[tp.Tuple[int, str]] = [
        (i.id, naive_bayes.stemmer.clear(i.title).lower())
        for i in s.query(News).filter(News.label == None).all()
    ]
    verbose_print("Got unlabeled news from database", 4)
    X: tp.List[str] = [i[1] for i in unclassified]
    verbose_print("Separated titles", 4)
    if not pathlib.Path(
        f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle"
    ).is_file():
        raise ValueError("Classifier is untrained! Something went wrong.")
    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/../model/model.pickle", "rb"
    ) as model_file:
        model = naive_bayes.bayes.NaiveBayesClassifier(alpha=alpha)
        model = pickle.load(model_file)
    verbose_print("Loaded model", 4)
    labels = model.predict(X)
    verbose_print("Predicted labels", 4)
    for i, e in enumerate(unclassified):
        extract = s.query(News).filter(News.id == e[0]).first()  # only one such news extract exists
        verbose_print(f"Selected extract {extract.title}", 4)
        extract.label = labels[i]
        verbose_print(f"Assigned label {extract.label}", 4)
        s.commit()
        verbose_print("committed to database", 4)
    return model


def score_model(model: NaiveBayesClassifier) -> float:
    verbose_print("Scoring model", 3)
    s = session()
    verbose_print("Acquired session lock", 4)
    rows = s.query(News).all()
    verbose_print("Got data from database", 4)
    stop_sign = int(0.7 * len(rows))  # train-to-test ratio is usually 70:30
    verbose_print("Determined dataset partitioning", 4)
    extracts: tp.List[str] = []
    labels: tp.List[str] = []
    for i in range(len(rows)):
        row = (
            s.query(News).filter(News.id == (i + 1)).first()
        )  # id is unique and enumerated from id
        extracts.append(row.title)
        labels.append(row.label)
    verbose_print("Created X and y", 4)
    extracts = [naive_bayes.stemmer.clear(x).lower() for x in extracts]
    verbose_print("Finished stemming extracts", 4)
    X_train, X_test = extracts[:stop_sign], extracts[stop_sign:]
    y_train, y_test = labels[:stop_sign], labels[stop_sign:]
    verbose_print("Partitioned into train and test", 4)
    model.fit(X_train, y_train)
    verbose_print("Trained model", 4)
    score = float(model.score(X_test, y_test))
    verbose_print(f"Classifier accuracy: {score}", 3)
    return score


def determine_alpha() -> float:
    verbose_print("Determining alphas", 1)
    optimal_alpha = 0.0
    max_score = 0.0
    clean_db()
    verbose_print("Cleaned database", 4)
    randomize(100)  # choice does not matter here
    verbose_print("Randomized labels", 4)
    for alpha in tqdm.tqdm([x / 100 for x in range(1, 101)], desc="Determining alpha"):
        verbose_print(f"Testing alpha {alpha}", 3)
        clean_model(alpha)
        model = fill_database(alpha)
        verbose_print("Predicted labels for database", 3)
        score = score_model(model)
        if score > max_score:
            max_score = score
            optimal_alpha = alpha

    return optimal_alpha


def determine_partition(alpha: float) -> int:
    verbose_print("Determining partitioning", 1)
    optimal_marker = 0
    max_score = 0.0
    s = session()
    verbose_print("Acquired session lock", 4)
    rows = s.query(News).all()
    verbose_print("Got news from database", 4)
    verbose_print(f"Length of data: {len(rows)}", 4)
    for marker in tqdm.tqdm(range(100, len(rows), 100), desc="Determining partitions (hundreds)"):
        verbose_print(f"Testing marker {marker}", 3)
        clean_db()
        randomize(marker)
        clean_model(alpha)
        model = fill_database(alpha)
        score = score_model(model)
        if score > max_score:
            max_score = score
            optimal_marker = marker
    for marker in tqdm.tqdm(
        range(optimal_marker - 100, optimal_marker + 100, 10), desc="Determining partitions (tens)"
    ):
        verbose_print(f"Testing marker {marker}", 3)
        clean_db()
        randomize(marker)
        clean_model(alpha)
        model = fill_database(alpha)
        score = score_model(model)
        if score > max_score:
            max_score = score
            optimal_marker = marker
    for marker in tqdm.tqdm(
        range(optimal_marker - 10, optimal_marker + 10), desc="Determining partitions (exact point)"
    ):
        verbose_print(f"Testing marker {marker}", 3)
        clean_db()
        randomize(marker)
        clean_model(alpha)
        model = fill_database(alpha)
        score = score_model(model)
        if score > max_score:
            max_score = score
            optimal_marker = marker

    return optimal_marker


def driver() -> tp.Tuple[float, int]:
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/results.txt", "w") as f:
        f.write(f"{datetime.datetime.now()} -> started testing\n")
        f.write(f"{datetime.datetime.now()} -> initialized parameters\n")
        optimal_alpha = determine_alpha()
        f.write(f"{datetime.datetime.now()} -> optimal alpha: {optimal_alpha}\n")
        verbose_print(f"Optimal alpha: {optimal_alpha}", 0)
        optimal_marker = determine_partition(optimal_alpha)
        f.write(f"{datetime.datetime.now()} -> optimal marker: {optimal_marker}\n")
        verbose_print(f"Optimal marking point: {optimal_marker}", 0)
        clean_db()
        randomize(optimal_marker)
        clean_model(optimal_alpha)
        model = fill_database(optimal_alpha)
        final_score = score_model(model)
        f.write(f"{datetime.datetime.now()} -> final score: {final_score}\n")
        verbose_print("Finished working!", 0)
        return (optimal_alpha, optimal_marker)


def move_score(alpha: float, marker: int) -> float:
    verbose_print("Shuffling data and rescoring model", 0)
    clean_db()
    verbose_print("Cleaned database", 2)
    randomize(marker)
    verbose_print("Randomized data", 2)
    clean_model(alpha)
    verbose_print("Reinitialized model", 3)
    model = fill_database(alpha)
    score = score_model(model)
    verbose_print("Reclassified data", 2)
    return score


def get_best_random(alpha: float, marker: int, attempts: int) -> None:
    verbose_print("Trying to reshuffle database for best score", 3)
    max_score: float = 0.0
    for i in tqdm.tqdm(range(attempts), desc="Attempting database reshuffles"):
        verbose_print(f"Reshuffle attempt {i+1}", 4)
        score: float = move_score(alpha, marker)
        verbose_print(f"Model score: {score}", 4)
        if score > max_score:
            verbose_print(f"Found maximum score", 4)
            max_score = score
            shutil.copy2(
                f"{os.path.dirname(os.path.realpath(__file__))}/../news.db",
                f"{os.path.dirname(os.path.realpath(__file__))}/best.db",
            )
    verbose_print("Finished trying for best score", 4)


def parse_results() -> tp.Tuple[float, int]:
    if not pathlib.Path("results.txt"):
        raise OSError(
            "No results yet. Please run this script without args to bruteforce parameters"
        )
    verbose_print("Results.txt exists. Parsing data...", 3)
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/results.txt") as f:
        alpha = 0.0
        marker = 0
        for i in f.readlines():
            if "optimal alpha" in i:
                verbose_print("Found alpha", 4)
                alpha = float(i[i.rfind(" ") + 1 : -1])
            elif "optimal marker" in i:
                verbose_print("Found marker", 4)
                marker = int(i[i.rfind(" ") + 1 : -1])
            else:
                pass
    verbose_print(f"Finished parsing data: alpha={alpha}, marker={marker}", 3)
    return alpha, marker


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="count", default=0, help="Verbosity level (default: 0)"
    )
    parser.add_argument(
        "-s",
        "--shuffle-database",
        action="store_true",
        default=False,
        help="Randomize database labels around data from results.txt",
    )
    parser.add_argument(
        "--attempts",
        action="store",
        default=100,
        type=int,
        required=False,
        help="Number of database reshuffle attempts (requires -m)",
    )
    namespace = parser.parse_args()
    VERBOSITY_LEVEL = namespace.verbose
    if (namespace.attempts != 100) and not namespace.shuffle_database:
        parser.error("-s required when attempts is set")
    if namespace.shuffle_database:
        alpha, marker = parse_results()
        verbose_print(f"Parsed out alpha and marker", 3)
        verbose_print(f"Reshuffling data to move score...", 2)
        get_best_random(alpha, marker, namespace.attempts)
    else:
        driver()
