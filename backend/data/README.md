# Data setup

Run `python scripts/download_data.py` from the repository root after installing dependencies. It downloads MovieLens latest-small from GroupLens, retaining movies.csv, links.csv and the original README.txt with usage terms. Ratings are not used in V1.

If the official HTTPS host is unavailable, run `python scripts/download_data.py --mirror`. This explicitly selects the public smanihwr/ml-latest-small mirror pinned to commit ba3cd91761e54faa64483456b619d1a1f4d70971. The local build used this fallback because the official host presented an expired certificate. TLS verification is never disabled. The script records the source and SHA-256 checksums in manifest.json.

Generated data files are ignored by Git; do not describe them as covered by the application code license. Original source and terms: https://grouplens.org/datasets/movielens/latest/. Read the downloaded README.txt before redistribution or other use. Expected snapshot: 9,742 movies, ending in 2018. Poster and overview enrichment is separate and optional.

## Series

Run `python scripts/download_series.py` for 20 pages of the TVmaze show index (IDs below 5000). Use `--pages N` to change coverage. The local snapshot contains 4704 series. `series.json` is a local cache; `series-manifest.json` records URLs, timestamp, checksum and scope. Both are ignored by Git. TVmaze data is provided under CC BY-SA: https://www.tvmaze.com/api#licensing. Source URLs are retained and linked in the UI. This data is separate from the application code and MovieLens data.
