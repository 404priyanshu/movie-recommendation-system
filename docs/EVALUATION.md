# Evaluation: descriptive sanity checks

Catalog: 9,742 movies; vector matrix: (9742, 8914).

| Profile | Mean genre Jaccard@10 | Min cosine | Max cosine |
|---|---:|---:|---:|
| science_fiction | 0.733 | 0.655 | 0.698 |
| animation | 0.963 | 0.820 | 0.912 |
| crime | 0.933 | 0.672 | 0.825 |

Genre Jaccard is intersection / union of recommendation genres and the favorites’ genre union. Because genres are input features, this is a circular sanity check, not evidence of user satisfaction. These are three hand-picked profiles, not a representative benchmark.

## Actual example

Favorites: Interstellar, Inception; IDs: [109487, 79132].

- Strange Days (1995): 0.698319 cosine; shared genres: Sci-Fi, Action, Crime, Drama, Mystery, Thriller. Terms: scifi=0.291049, mystery=0.143157, crime=0.093781, action=0.070105, thriller=0.068286, drama=0.031942
- One, The (2001): 0.687250 cosine; shared genres: Sci-Fi, Action, Thriller. Terms: scifi=0.465777, action=0.112192, thriller=0.109281
- Next (2007): 0.687250 cosine; shared genres: Sci-Fi, Action, Thriller. Terms: scifi=0.465777, action=0.112192, thriller=0.109281

## What the inspection taught us

An initial version treated IMAX as a genre. Its rarity made it dominate blockbuster matches. We excluded this presentation format from content features. This is feature engineering informed by qualitative inspection, not a statistically validated improvement.

Title vocabulary can privilege sequels and odd lexical matches; genre metadata misses tone, direction and quality. A richer corpus and blind human judgments would be the next quality checks. No held-out precision, recall, or accuracy is claimed. The notebook plots the full candidate score distribution, which is more informative than only looking at the ten winners.

Regenerate with `python scripts/evaluate.py`. Full machine-readable output: `evaluation.json`.
