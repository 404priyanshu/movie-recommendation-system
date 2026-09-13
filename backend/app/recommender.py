"""A small, explainable content-based recommender. No LLM or ratings model."""
from collections import Counter
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .data import normalize

class Recommender:
    def __init__(self, movies: pd.DataFrame):
        self.movies = movies
        self.id_to_index = {int(mid): i for i, mid in enumerate(movies.movieId)}
        # A column represents a word; a row represents a movie. TF-IDF gives
        # less weight to words appearing throughout the catalog. L2 normalization
        # makes each movie vector have length 1. The matrix stays sparse.
        self.vectorizer = TfidfVectorizer(stop_words='english', strip_accents='unicode', dtype=np.float64)
        self.matrix = self.vectorizer.fit_transform(movies.features)
        self.terms = self.vectorizer.get_feature_names_out()

    def movie(self, index: int) -> dict:
        row = self.movies.iloc[index]
        return {'id': int(row.movieId), 'title': row.title,
                'year': int(row.year) if pd.notna(row.year) else None,
                'genres': row.genres, 'media_type': row.get('media_type', 'movie'),
                'poster_url': row.get('poster_url'), 'overview': row.get('overview'),
                'source_url': row.get('source_url'), 'platform': row.get('platform'),
                'netflix_original': bool(row.get('netflix_original', False))}

    def search(self, query: str, limit: int = 8) -> list[dict]:
        query = normalize(query)
        if not query:
            return []
        matches = [i for i, title in enumerate(self.movies.search_title) if query in title]
        matches.sort(key=lambda i: (not self.movies.iloc[i].search_title.startswith(query), len(self.movies.iloc[i].title), i))
        return [self.movie(i) for i in matches[:limit]]

    def recommend(self, movie_ids: list[int], limit: int = 10, media_type: str = 'all') -> list[dict]:
        if media_type not in ('all', 'movie', 'series', 'netflix'):
            raise ValueError('Invalid media type.')
        ids = list(dict.fromkeys(movie_ids))
        if not ids:
            raise ValueError('Select at least one movie.')
        missing = [mid for mid in ids if mid not in self.id_to_index]
        if missing:
            raise ValueError(f'Unknown movie IDs: {missing}')
        indices = [self.id_to_index[mid] for mid in ids]
        # Average favorite vectors: each favorite gets an equal vote in taste.
        taste = np.asarray(self.matrix[indices].mean(axis=0))
        # Cosine measures direction, rather than vector length. With nonnegative
        # TF-IDF features it lies in [0, 1]. It is NOT a probability of liking.
        scores = np.clip(cosine_similarity(taste, self.matrix).ravel(), 0, 1)
        scores[indices] = -1  # Never recommend a selected movie again.
        # Stable sorting gives deterministic movie-ID order for exact ties.
        ranked = np.argsort(-scores, kind='stable')
        genre_counts = Counter(g for i in indices for g in self.movies.iloc[i].genres)
        taste_unit = taste.ravel() / max(np.linalg.norm(taste), 1e-12)
        results = []
        for index in ranked:
            if scores[index] <= 0 or len(results) >= limit:
                break
            item = self.movie(int(index))
            if media_type == 'netflix' and not item['netflix_original']:
                continue
            if media_type in ('movie', 'series') and item['media_type'] != media_type:
                continue
            overlap = sorted(set(item['genres']) & genre_counts.keys(), key=lambda g: (-genre_counts[g], g))
            # Per-term products sum to cosine similarity. These contributions
            # are faithful local explanations of the actual ranking calculation.
            contributions = self.matrix[index].multiply(taste_unit).tocsr()
            ordered = sorted(zip(contributions.indices, contributions.data), key=lambda pair: (-pair[1], pair[0]))
            features = [{'term': str(self.terms[j]), 'contribution': float(v)} for j, v in ordered if v > 0][:6]
            reasons = [f'{g} appears in {genre_counts[g]} of your {len(ids)} favorites.' for g in overlap]
            reasons.append('Shared TF-IDF terms contribute to the cosine similarity with your averaged taste vector.')
            results.append({**item, 'score': float(scores[index]), 'shared_genres': overlap,
                            'shared_features': features, 'reasons': reasons,
                            'explanation': 'Shared tastes: ' + ', '.join(overlap) + '.' if overlap else 'Connected through shared title terms.',
                            'selected_titles': [self.movies.iloc[i].title for i in indices]})
        return results
