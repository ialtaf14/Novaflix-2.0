"""
display.py — data loading helpers, no Streamlit dependency.
Uses functools.lru_cache for in-process RAM caching.
"""
import os
import pickle
from functools import lru_cache

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@lru_cache(maxsize=1)
def load_dataframes():
    """Load movies, movies2 and new_df from pickle files (cached in RAM)."""
    pickle_file_path = r'Files/new_df_dict.pkl'
    if os.path.exists(pickle_file_path):
        with open(r'Files/movies_dict.pkl', 'rb') as f:
            movies = pd.DataFrame.from_dict(pickle.load(f))
        with open(r'Files/movies2_dict.pkl', 'rb') as f:
            movies2 = pd.DataFrame.from_dict(pickle.load(f))
        with open(pickle_file_path, 'rb') as f:
            new_df = pd.DataFrame.from_dict(pickle.load(f))
        return new_df, movies, movies2
    else:
        from processing import preprocess
        movies, new_df, movies2 = preprocess.read_csv_to_df()
        return new_df, movies, movies2


# Simple in-memory cache keyed by column name
_similarity_cache: dict = {}

def load_similarity(col_name: str, new_df):
    """Load or compute a cosine-similarity matrix for the given column."""
    if col_name in _similarity_cache:
        return _similarity_cache[col_name]

    pickle_file_path = fr'Files/similarity_tags_{col_name}.pkl'
    if os.path.exists(pickle_file_path):
        with open(pickle_file_path, 'rb') as f:
            result = pickle.load(f)
    else:
        cv = CountVectorizer(max_features=5000, stop_words='english')
        vec_tags = cv.fit_transform(new_df[col_name]).toarray()
        result = cosine_similarity(vec_tags)

    _similarity_cache[col_name] = result
    return result


class Main:
    """Context-manager wrapper that pre-warms all data caches on entry."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __init__(self):
        self.new_df  = None
        self.movies  = None
        self.movies2 = None

    def getter(self):
        return self.new_df, self.movies, self.movies2

    def main_(self):
        self.new_df, self.movies, self.movies2 = load_dataframes()
        # Pre-warm similarity matrices
        for col in ('tags', 'genres', 'keywords', 'tcast', 'tprduction_comp'):
            load_similarity(col, self.new_df)