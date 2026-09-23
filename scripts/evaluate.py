"""Compare the previous title/genre ranker with the current story/genre ranker.

The fixed judgments are intentionally small and subjective. This script never
changes them or fits weights against them. Run with a locally downloaded TMDB
catalog: python scripts/evaluate.py [--catalog PATH].
"""
import argparse
import json
import math
from datetime import date
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.data import load_catalog, normalize
from backend.app.recommender import Recommender


def old_rank(model: Recommender, favorites: list[int], limit: int = 10) -> list[int]:
    """Frozen pre-change formula; independent of the current model constants."""
    movies = model.movies
    features = [' '.join([normalize(g.replace('-', '')) for g in genres] * 3 + [normalize(title)])
                for title, genres in zip(movies.title, movies.genres)]
    matrix = TfidfVectorizer(stop_words='english', strip_accents='unicode', dtype=np.float64).fit_transform(features)
    indices = [model.id_to_index[mid] for mid in favorites]
    taste = np.asarray(matrix[indices].mean(axis=0))
    content = cosine_similarity(taste, matrix).ravel()
    popularity = movies.popularity.astype(float).clip(lower=0)
    popularity = (popularity / popularity.max()).to_numpy() if popularity.max() else np.zeros(len(movies))
    age = (date.today().year - movies.year.fillna(date.today().year - 100)).clip(lower=0)
    recency = np.exp(-age.to_numpy() * np.log(2) / 6)
    scores = 0.7 * content + 0.15 * popularity + 0.15 * recency
    scores[indices] = -1
    return [int(movies.iloc[i].movieId) for i in np.argsort(-scores, kind='stable') if scores[i] > 0][:limit]


def ndcg_at_10(ranked: list[int], relevant: set[int]) -> float:
    gain = sum(1 / math.log2(position + 2) for position, mid in enumerate(ranked[:10]) if mid in relevant)
    ideal = sum(1 / math.log2(position + 2) for position in range(min(10, len(relevant))))
    return gain / ideal if ideal else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--catalog', type=Path, default=ROOT / 'backend/data/tmdb_catalog.json')
    args = parser.parse_args()
    model = Recommender(load_catalog(args.catalog))
    judgments = json.loads((ROOT / 'docs/relevance_judgments.json').read_text())
    print(f"Catalog: {len(model.movies)} titles; {len(judgments['profiles'])} fixed profiles")
    print('| Profile | Previous NDCG@10 | Revised NDCG@10 | Previous relevant IDs in top 10 | Revised relevant IDs in top 10 |')
    print('|---|---:|---:|---|---|')
    totals = []
    for profile in judgments['profiles']:
        favorites, relevant = profile['favorites'], set(profile['relevant'])
        if any(mid not in model.id_to_index for mid in set(favorites) | relevant):
            raise ValueError(f"Profile {profile['name']} refers to IDs absent from this catalog")
        previous = old_rank(model, favorites)
        revised = [item['id'] for item in model.recommend(favorites, 10)]
        before, after = ndcg_at_10(previous, relevant), ndcg_at_10(revised, relevant)
        totals.append((before, after))
        print(f"| {profile['name']} | {before:.3f} | {after:.3f} | {', '.join(map(str, sorted(set(previous) & relevant))) or 'none'} | {', '.join(map(str, sorted(set(revised) & relevant))) or 'none'} |")
    before = sum(row[0] for row in totals) / len(totals)
    after = sum(row[1] for row in totals) / len(totals)
    print(f'\nMean NDCG@10: previous {before:.3f}; revised {after:.3f}; delta {after-before:+.3f}')
    print('These hand-selected judgments are diagnostic only; they do not establish general recommendation quality.')


if __name__ == '__main__':
    main()
