import typing as tp

import nltk


def clear(s: str) -> str:
    try:
        nltk.data.find("punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)
    try:
        nltk.data.find("stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)
    stemmer = nltk.stem.SnowballStemmer("english")
    tokens: tp.List[str] = [
        stemmer.stem(token)
        for token in nltk.word_tokenize(s)
        if token.isalnum() and not token in nltk.corpus.stopwords.words("english")
    ]
    return " ".join(tokens)
