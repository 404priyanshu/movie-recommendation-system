# Series update verification

The app supports combined movie/series favorites and All / Movies / Series / Netflix Originals candidate filters. Verified in the Codex in-app browser: Breaking Bad search → series selection → ten series-only results → actual term explanation → add Interstellar → Movies filter → ten movie-only results → remove Interstellar → regenerate series. Posters, plain-text summaries, source attribution and type labels render. Mobile content width matches the 390px viewport. Browser error logs are empty.

Backend: 22 tests pass, including cross-source ID uniqueness, mixed favorites, media filters, series exclusion, unified search/API validation and ensuring series do not call the TMDB movie endpoint. ESLint, TypeScript and production build pass. Original movie-only numerical examples are explicitly labeled as a baseline; live scores change with the joint vocabulary.

The default series catalog is a bounded TVmaze index cache; see its manifest for exact coverage. Expanding the data changes IDF weights and therefore scores, without changing the recommendation algorithm.

---

# Local verification

Environment: macOS, Python 3.14.6, Node 26.5.0, Next.js production server at http://127.0.0.1:3000 and FastAPI at http://127.0.0.1:8000. Verified 2026-09-13 using the Codex in-app browser through CUA; no external browser fallback.

| Check | Result |
|---|---|
| Page identity and meaningful initial content | PASS |
| No framework error overlay | PASS |
| Browser error/warning logs | PASS: empty |
| Search Interstellar and Inception | PASS: real backend matches selected |
| Multiple favorites → Find My Movies | PASS: ten cards, Strange Days first at 69.8% |
| Why this movie disclosure | PASS: actual term contributions and selected titles |
| Remove Inception | PASS: old cards immediately cleared |
| Generate again | PASS: ten new results; Alien from L.A. first for Interstellar alone |
| No-result query | PASS: explicit no-match feedback |
| ArrowDown + Enter search selection | PASS |
| Mobile at 390 × 844 | PASS: ten cards; document width = viewport width, 390px |
| How it works page | PASS: correct route and six educational steps |
| Desktop at 1440 × 1000 | PASS: concept composition and controls visually checked |
| Python behavior/API tests | PASS: 18 tests |
| ESLint / TypeScript / production build | PASS |
| Notebook execution | PASS: 28 cells, saved outputs and plots |

Two warnings remain from dependencies in the test runner: Starlette's httpx transition and an AnyIO alias deprecation. They do not indicate app failures. No lint warnings remain. Optional TMDB network failure was mocked; live TMDB success was not verified because no key was supplied. Other browsers and assistive technology were not exhaustively tested.

The initial IMAX-dominated recommendations led to a preprocessing correction and a regression test. An intermediate-width headline wrapping issue was corrected with a fluid type scale. Final screenshots were visually compared with docs/design-concept.png. The concept's preselected sample chips become a true empty initial state in the working app. Standalone generated art follows the same space/desert/mountain triptych direction.

The in-app full-page screenshot exporter produced duplicated/scaled regions; saved portfolio screenshots use its normal viewport capture instead. This was a capture artifact, not duplicated DOM content.
