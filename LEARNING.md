# Learning CineMatch, one idea at a time

## Update: series support

The live website now uses `load_catalog()` to combine 9,742 movies and 4,721 series. A curated boolean marks 25 well-known Netflix originals and powers the Netflix Originals result filter. Platform/original status is filtering and display metadata; it is not added to TF-IDF text, so it cannot inflate similarity. The notebook and numerical walkthrough below remain a reproducible movie-only baseline using `load_movies()`. Joint-catalog IDF weights differ, so do not expect the live app to reproduce baseline scores exactly.

TVmaze supplies series metadata without a key. We map Science-Fiction to Sci-Fi, strip HTML from display summaries, and use the same title/genre features for both sources. Summaries and posters do not influence ranking. A series ID is 1,000,000,000 plus its TVmaze ID, avoiding collisions with movie IDs.

The recommendation type filter restricts candidates after scores are computed. It does not refit the vocabulary or discard favorites of the other type. Try selecting Breaking Bad and a crime movie, then compare Series versus Movies results. The download defaults to 20 pages (show IDs below 5,000); it is a bounded catalog, not every series ever released. Data is credited to TVmaze under CC BY-SA.


You built a content-based recommendation system, not a model that predicts star ratings. The vocabulary and inverse-document-frequency weights are learned from metadata. It is an information-retrieval / unsupervised feature-extraction project; there are no supervised target labels.

## 1. What is a recommendation system?

It ranks a large set of items into a short list that might be useful to a person. CineMatch starts with movies you explicitly like and finds movies with similar metadata. It does not know who you are or remember preferences after the page is refreshed.

## 2. Content-based versus collaborative filtering

Content-based: “You selected science-fiction movies; here are movies with similar features.” It needs item metadata and a few favorites.

Collaborative: “People who liked these movies also liked these other ones.” It needs a user–item interaction table. MovieLens includes ratings, but V1 deliberately does not download or use them. That keeps the first model easy to understand.

## 3. What is a vector?

A vector is an ordered list of numbers. If our vocabulary is [scifi, space, drama], [1, 1, 0] represents a movie mentioning science fiction and space, but not drama. Position matters: every movie must use the same vocabulary order. The real catalog has 8,914 vocabulary terms, not just three.

## 4. How does text become numbers?

Study `backend/app/data.py`. We extract the year, remove it from the title, fill missing values, split genres, remove punctuation, and lowercase. Sci-Fi becomes scifi. We remove IMAX because a format is not story content. A movie without a genre gets an empty list, not a fake genre. Titles remain useful but can produce misleading lexical matches.

Each genre is repeated three times. This weights genres more heavily than incidental title words. It is a manually chosen hyperparameter, not something the model discovered or a value proven optimal.

Interstellar becomes:

```text
adventure drama scifi adventure drama scifi adventure drama scifi interstellar
```

Inception becomes:

```text
action crime mystery scifi thriller action crime mystery scifi thriller action crime mystery scifi thriller inception
```

## 5. What is TF-IDF?

TF is term frequency: how often a word occurs in one movie’s text. IDF is inverse document frequency: a word that appears in almost every movie is less distinctive. Scikit-learn’s default smoothed formula is:

```text
idf(term) = log((1 + number_of_movies) / (1 + movies_containing_term)) + 1
raw_weight = term_count * idf(term)
final_vector = raw_weights / length(raw_weights)
```

`TfidfVectorizer` also removes English stop words, strips accents, builds a shared vocabulary and returns a sparse matrix. Sparse means we store nonzero entries efficiently, because most movies contain only a few vocabulary words. Do not convert the entire catalog to a dense array just to inspect it.

## 6. What do this project’s vectors represent?

The matrix has 9,742 rows (movies) and 8,914 columns (terms) for the downloaded snapshot. A large scifi value means that feature is strongly represented in that movie after count and IDF weighting. It does not mean the model understands space travel. This is a bag-of-words representation: no plot understanding, contextual meaning, or language generation.

## 7. What is cosine similarity, and why use it?

Imagine each vector as an arrow. Cosine compares the direction of two arrows, not their length:

```text
cosine(a, b) = dot(a, b) / (length(a) * length(b))
```

Shared nonzero terms increase the dot product. With our nonnegative TF-IDF values, cosine is between 0 and 1. Two identical nonzero vectors score 1; no shared terms scores 0. Different movies can have identical vectors after preprocessing. A zero vector has no useful terms and scikit-learn treats its similarity as zero.

This works for our purpose because we want comparable feature patterns, not simply long titles. It is still limited to the words we supply. A 69.8% match is cosine 0.698, **not** a 69.8% probability that you will enjoy the movie.

## 8. How do several favorites form a taste profile?

Find each favorite’s row using its ID. Average the rows:

```text
taste = (vector_of_favorite_1 + vector_of_favorite_2) / 2
```

Each favorite gets an equal vote because movie rows are normalized first. Terms shared across favorites can become more prominent. The average is not necessarily unit length; cosine normalizes it when comparing. Duplicate IDs are removed so selecting a movie twice cannot give it two votes. The API permits one to five favorites; three to five is a UX suggestion, not a mathematical requirement.

## 9. Ranking and excluding selected movies

Compute one cosine score per movie against the taste profile. Mark already-selected movies with -1, sort descending, and keep up to ten positive scores. Stable sorting on a catalog sorted by movie ID resolves ties reproducibly. Excluding selected films makes results useful for discovery. We do not inflate scores with min–max scaling, popularity, random numbers, or external recommendation APIs.

## 10. Walk through an actual recommendation

Favorites: Interstellar (109487) and Inception (79132). The resulting top recommendation in this snapshot is Strange Days (1995), with cosine **0.698319** (displayed as **69.8% match**).

The strongest shared term contributions are:

| Term | Contribution to cosine |
|---|---:|
| scifi | 0.291049 |
| mystery | 0.143157 |
| crime | 0.093781 |
| action | 0.070105 |
| thriller | 0.068286 |
| drama | 0.031942 |

Each contribution is the recommended movie’s term weight multiplied by the normalized taste profile’s weight for that term. Their sum, allowing for printed rounding, gives 0.698319. The API returns these actual products. The explanation also counts genres across favorites. It cannot truthfully claim shared directors or cerebral themes, because those features are not in V1.

Reproduce these values with `python scripts/evaluate.py` and notebook section 11. See `docs/evaluation.json` for full precision and more profiles.

## 11. How the website and API fit together

React keeps favorites, search state and results in memory. Search waits 250 ms after typing before requesting matches; an AbortController cancels obsolete requests. The search supports arrow keys, Enter and Escape. Removing or adding a favorite clears old recommendations and cancels pending work.

The browser requests `/api/movies/search` and `/api/recommend` from Next.js. A Next.js rewrite proxies these to FastAPI, so browser requests remain same-origin and API keys never enter client code. FastAPI fits one model at startup, validates requests with Pydantic, calls the separate recommender, and serializes structured results. Unknown IDs return 400; malformed bodies return 422.

TMDB enrichment, if enabled, uses the MovieLens-to-TMDB ID mapping to add posters and synopses only after ranking. A timeout or bad key falls back to no synopsis and labeled original genre artwork. This is deliberate: turning on a display feature should not silently change the model you studied.

## 12. Important files and study order

| Order | File | What to understand |
|---|---|---|
| 1 | `notebooks/recommender_exploration.ipynb` | Run and inspect each stage; experiment with numbers. |
| 2 | `backend/app/data.py` | Missing values, year extraction, normalization, feature construction. |
| 3 | `backend/app/recommender.py` | Vocabulary fitting, sparse matrix, averaging, cosine, ranking, explanations. |
| 4 | `backend/app/schemas.py` | API contracts and input validation. |
| 5 | `backend/app/main.py` | Startup lifecycle and endpoint orchestration. |
| 6 | `backend/tests/test_recommender.py` | Behavior guarantees and an independent manual cosine calculation. |
| 7 | `frontend/components/discovery.tsx` | Favorites and request state; stale-result prevention. |
| 8 | `frontend/components/movie-search.tsx` | Debounced autocomplete, cancellation and keyboard controls. |
| 9 | `frontend/components/movie-card.tsx` | Real scores, image fallback and explanation disclosure. |
| 10 | `frontend/lib/api.ts` | Typed HTTP requests and error handling. |
| 11 | `backend/app/enrichment.py` | Optional external metadata with bounded timeouts and cache. |
| 12 | `scripts/evaluate.py` | Reproducible descriptive analysis, not predictive accuracy. |

`frontend/app/page.tsx` composes the main page. `layout.tsx` owns shared navigation and footer. `globals.css` contains design tokens and responsive layouts with Tailwind available for utilities. `how-it-works/page.tsx` teaches the pipeline. `scripts/download_data.py` records data provenance. `next.config.ts` connects the frontend to the backend.

## 13. Limitations you should be comfortable explaining

- Similarity bubbles: familiar genres crowd out surprising discoveries.
- New movies need metadata, and this catalog stops in 2018.
- No learning from other users, no accounts, and no persistent history.
- Genre overlap cannot capture acting, tone, directors or quality.
- Rare words and sequels can dominate similarity. Even stop-word removal can matter.
- MovieLens has limited metadata and English-oriented preprocessing favors some titles.
- The model is fitted to the whole catalog for retrieval. There is no supervised train/test split or accuracy claim.
- Genre Jaccard overlap uses the same features the model ranks with. It is a sanity check, not independent validation.
- Display synopses from TMDB are not model inputs. Adding them later requires deliberate refitting and evaluation.
- API startup recomputes TF-IDF; fine for this size, but large catalogs need an offline build and versioned artifacts.

## 14. Ten interview / viva questions

1. How does content-based filtering differ from collaborative filtering?
2. What are TF and IDF, and why do you normalize TF-IDF rows?
3. What does one row and one column in your matrix represent?
4. Why use cosine similarity rather than raw dot product or Euclidean distance?
5. How do multiple favorites become one user profile?
6. Why is 70% match not a probability or an accuracy metric?
7. How are selected movies excluded and ties resolved?
8. How can you prove that the explanation reflects the actual model calculation?
9. Why did you remove IMAX, and how would you validate other feature changes?
10. How would you evaluate and extend this into a collaborative or hybrid recommender?

## 15. What to implement yourself next

First, add a **genre-weight experiment** in the notebook. Compare weights 1, 2 and 3 for five fixed favorite lists; write down qualitative differences and failures. Keep the test conditions fixed. Then add a meaningful regression test for a behavior you care about, such as favorite-order invariance.

After that, collect a small set of human relevance judgments and learn Precision@K, Recall@K and NDCG. Use a held-out set to compare feature choices. Only then explore MovieLens ratings, user–item matrices, nearest-neighbor collaborative filtering, matrix factorization, and a hybrid ranker. Implement the first experiment yourself rather than asking an assistant to complete it: the reasoning and observations are the portfolio story.
