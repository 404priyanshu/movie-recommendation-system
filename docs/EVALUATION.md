# Recommendation relevance check

The fixed judgments in [`relevance_judgments.json`](relevance_judgments.json) were chosen from the locally downloaded TMDB catalog before calculating the revised scores. Each profile uses one favorite and a short list of subjectively related titles. `scripts/evaluate.py` independently reconstructs the previous title and genre model, runs the current story and genre model against the same catalog, and computes binary NDCG@10.

The catalog used here contained 9,195 titles and was downloaded on 2026-09-13. Run `python scripts/evaluate.py` after downloading the catalog to reproduce results. Catalog refreshes and the passage of time can change rankings because popularity and recency are score inputs.

| Profile | Previous NDCG@10 | Revised NDCG@10 | Previous relevant IDs in top 10 | Revised relevant IDs in top 10 |
|---|---:|---:|---|---|
| space survival | 0.000 | 0.000 | none | none |
| crime series | 0.000 | 0.000 | none | none |
| animated family stories | 0.491 | 0.699 | 863, 10193, 301528 | 863, 10193, 301528 |
| murder mystery | 0.469 | 0.469 | 661374 | 661374 |
| **Mean** | **0.240** | **0.292** | | |

The mean increased by **0.052**, but the gain came from one profile. This is a small, hand-selected diagnostic and does not show a general or statistically reliable improvement. In particular, single-favorite plot summaries still miss semantically related titles that use different words. The current model also prefers titles with at least 100 TMDB votes and excludes future release years; these guardrails remove sparse catalog entries but can hide worthwhile niche titles.

The executed notebook and its original examples document the older MovieLens model. They are retained as a historical learning artifact and are not an evaluation of the live TMDB application.
