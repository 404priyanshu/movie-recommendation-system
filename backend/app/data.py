"""Load and prepare MovieLens metadata, independently of the web API."""
from pathlib import Path
import re
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'

def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', text.casefold())).strip()

def content_features(title: str, genres: list[str]) -> str:
    # Keep Sci-Fi and Film-Noir as single tokens; repeat genres to emphasize
    # content over incidental title words. This is an explicit design choice.
    genre_tokens = [normalize(g.replace('-', '')) for g in genres]
    return ' '.join(genre_tokens * 3 + [normalize(title)])

def load_movies(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    if not (data_dir / 'movies.csv').exists():
        raise FileNotFoundError('MovieLens is missing. Run: python scripts/download_data.py')
    movies = pd.read_csv(data_dir / 'movies.csv').drop_duplicates('movieId').copy()
    movies['title'] = movies['title'].fillna('Untitled')
    movies['year'] = movies['title'].str.extract(r'\((\d{4})\)\s*$')[0].apply(lambda x: int(x) if pd.notna(x) else None)
    movies['title'] = movies['title'].str.replace(r'\s*\(\d{4}\)\s*$', '', regex=True)
    # IMAX is a presentation format, not story content; otherwise its rarity
    # can dominate TF-IDF similarity among recent blockbusters.
    movies['genres'] = movies['genres'].fillna('').apply(lambda value: [g for g in value.split('|') if g and g not in ('(no genres listed)', 'IMAX')])
    movies['search_title'] = movies['title'].map(normalize)
    movies['features'] = movies.apply(lambda row: content_features(row.title, row.genres), axis=1)
    links = pd.read_csv(data_dir / 'links.csv', usecols=['movieId', 'tmdbId'])
    return movies.merge(links, on='movieId', how='left').sort_values('movieId').reset_index(drop=True)

# Series use a separate numeric namespace so a TVmaze ID can never be confused
# with a MovieLens ID. Existing movie IDs and API requests remain compatible.
SERIES_ID_OFFSET = 1_000_000_000

def load_catalog(data_dir: Path = DATA_DIR) -> pd.DataFrame:
    """Use the same title/genre features for both media types for fair comparison."""
    import json
    from html import unescape

    movies = load_movies(data_dir)
    movies['media_type'] = 'movie'
    movies['poster_url'] = None
    movies['overview'] = None
    movies['source_url'] = None
    series_path = data_dir / 'series.json'
    if not series_path.exists():
        raise FileNotFoundError('Series metadata is missing. Run: python scripts/download_series.py')
    records = []
    for show in json.loads(series_path.read_text()):
        title = show.get('name') or 'Untitled'
        # Map TVmaze's genre spelling into the MovieLens vocabulary.
        genres = list(dict.fromkeys('Sci-Fi' if genre == 'Science-Fiction' else genre for genre in (show.get('genres') or [])))
        premiered = show.get('premiered') or ''
        image = show.get('image') or {}
        summary = unescape(re.sub(r'<[^>]+>', '', show.get('summary') or '')).strip()
        records.append({'movieId': SERIES_ID_OFFSET + show['id'], 'title': title,
                        'year': int(premiered[:4]) if re.match(r'^\d{4}', premiered) else None,
                        'genres': genres, 'search_title': normalize(title),
                        'features': content_features(title, genres), 'tmdbId': None,
                        'media_type': 'series', 'poster_url': image.get('medium'),
                        'overview': summary or None, 'source_url': show.get('url'),
                        'platform': ((show.get('webChannel') or show.get('network') or {}).get('name')),
                        'netflix_original': bool(show.get('netflix_original', False))})
    movies['platform'] = None
    movies['netflix_original'] = False
    catalog = pd.concat([movies, pd.DataFrame(records)], ignore_index=True)
    if catalog.movieId.duplicated().any():
        raise ValueError('Duplicate catalog IDs detected.')
    return catalog.sort_values('movieId').reset_index(drop=True)
