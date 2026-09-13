"""Descriptive sanity checks, NOT predictive accuracy or a held-out benchmark."""
from pathlib import Path
import sys
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from backend.app.data import load_movies
from backend.app.recommender import Recommender

model = Recommender(load_movies())
profiles = {'science_fiction': ['Interstellar', 'Inception'], 'animation': ['Toy Story', 'Finding Nemo'], 'crime': ['Godfather, The', 'Goodfellas']}
report = {'catalog_size':len(model.movies), 'matrix_shape':list(model.matrix.shape), 'profiles':{}}
for name, titles in profiles.items():
    ids = [model.search(title)[0]['id'] for title in titles]
    results = model.recommend(ids)
    genres = set(g for mid in ids for g in model.movies.iloc[model.id_to_index[mid]].genres)
    overlaps = [len(genres & set(r['genres'])) / max(len(genres | set(r['genres'])), 1) for r in results]
    report['profiles'][name] = {'favorites':titles, 'ids':ids, 'mean_genre_jaccard':float(np.mean(overlaps)), 'score_min':min(r['score'] for r in results), 'score_max':max(r['score'] for r in results), 'results':results}
Path('docs/evaluation.json').write_text(json.dumps(report, indent=2))
example = report['profiles']['science_fiction']
lines = ['# Evaluation: descriptive sanity checks', '', f'Catalog: {len(model.movies):,} movies; vector matrix: {model.matrix.shape}.', '', '| Profile | Mean genre Jaccard@10 | Min cosine | Max cosine |', '|---|---:|---:|---:|']
for name, row in report['profiles'].items():
    lines.append(f"| {name} | {row['mean_genre_jaccard']:.3f} | {row['score_min']:.3f} | {row['score_max']:.3f} |")
lines += ['', 'Genre Jaccard is intersection / union of recommendation genres and the favorites’ genre union. Because genres are input features, this is a circular sanity check, not evidence of user satisfaction. These are three hand-picked profiles, not a representative benchmark.', '', '## Actual example', '', f"Favorites: {', '.join(example['favorites'])}; IDs: {example['ids']}.", '']
for item in example['results'][:3]:
    lines += [f"- {item['title']} ({item['year']}): {item['score']:.6f} cosine; shared genres: {', '.join(item['shared_genres'])}. Terms: " + ', '.join(f"{f['term']}={f['contribution']:.6f}" for f in item['shared_features'])]
lines += ['', '## What the inspection taught us', '', 'An initial version treated IMAX as a genre. Its rarity made it dominate blockbuster matches. We excluded this presentation format from content features. This is feature engineering informed by qualitative inspection, not a statistically validated improvement.', '', 'Title vocabulary can privilege sequels and odd lexical matches; genre metadata misses tone, direction and quality. A richer corpus and blind human judgments would be the next quality checks. No held-out precision, recall, or accuracy is claimed. The notebook plots the full candidate score distribution, which is more informative than only looking at the ten winners.', '', 'Regenerate with `python scripts/evaluate.py`. Full machine-readable output: `evaluation.json`.']
Path('docs/EVALUATION.md').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
