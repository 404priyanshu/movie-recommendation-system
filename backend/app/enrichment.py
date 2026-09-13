"""Optional TMDB display metadata. Failure never changes recommendations."""
from functools import lru_cache
import os
import httpx
import pandas as pd

@lru_cache(maxsize=2048)
def details(tmdb_id: int, key: str) -> dict:
    try:
        response = httpx.get(f'https://api.themoviedb.org/3/movie/{tmdb_id}', params={'api_key': key}, timeout=2)
        response.raise_for_status()
        data = response.json()
        path = data.get('poster_path')
        return {'overview': data.get('overview') or None,
                'poster_url': f'https://image.tmdb.org/t/p/w500{path}' if isinstance(path, str) and path.startswith('/') else None}
    except (httpx.HTTPError, ValueError):
        return {}

def enrich(movie: dict, movies: pd.DataFrame) -> dict:
    if movie.get('media_type') == 'series':
        return movie  # TVmaze already supplies series display metadata.
    key = os.getenv('TMDB_API_KEY')
    if not key:
        return movie
    tmdb_id = movies.loc[movies.movieId == movie['id'], 'tmdbId'].iloc[0]
    return {**movie, **details(int(tmdb_id), key)} if pd.notna(tmdb_id) else movie
