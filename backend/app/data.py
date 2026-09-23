"""Load and prepare the TMDB catalog, independently of the web API."""
from pathlib import Path
import json
import re
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / 'data'
SERIES_ID_OFFSET = 1_000_000_000

def normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', re.sub(r'[^\w\s]', ' ', text.casefold())).strip()

def content_features(title: str, genres: list[str], overview: str | None = None) -> str:
    """Represent story and genre, never franchise or title words.

    Very short synopses carry little story information, so those titles fall
    back to their genres. Keep ``title`` for callers of the old helper.
    """
    genre_tokens = [normalize(g.replace('-', '')) for g in genres]
    story = normalize(overview) if isinstance(overview, str) else ''
    if len(story.split()) < 6:
        story = ''
    return ' '.join(token for token in genre_tokens * 3 + [story] if token)

def load_catalog(data_dir: Path | None = None) -> pd.DataFrame:
    data_dir = data_dir or DATA_DIR
    path = data_dir if data_dir.is_file() else data_dir / 'tmdb_catalog.json'
    if not path.exists():
        raise FileNotFoundError('TMDB catalog is missing. Run: python scripts/download_tmdb.py (needs TMDB_API_KEY)')
    records = json.loads(path.read_text())
    catalog = pd.DataFrame.from_records(records).rename(columns={'id': 'movieId'})
    catalog['search_title'] = catalog['title'].map(normalize)
    catalog['features'] = catalog.apply(lambda row: content_features(row.title, row.genres, row.overview), axis=1)
    if catalog.movieId.duplicated().any():
        raise ValueError('Duplicate catalog IDs detected.')
    return catalog.sort_values('movieId').reset_index(drop=True)
