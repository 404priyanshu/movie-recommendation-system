"use client";
import { useRef, useState, useEffect } from "react";
import { ArrowRight, Clapperboard, X, LoaderCircle } from "lucide-react";
import MovieSearch from "./movie-search";
import MovieCard from "./movie-card";
import { recommendMovies } from "@/lib/api";
import type { Movie, Recommendation, MediaFilter } from "@/types/movie";
export default function Discovery() {
  const [mediaType, setMediaType] = useState<MediaFilter>("all");
  const [selected, setSelected] = useState<Movie[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [error, setError] = useState("");
  const pending = useRef<AbortController | null>(null);
  useEffect(() => () => pending.current?.abort(), []);
  function changeSelection(next: Movie[]) {
    pending.current?.abort();
    setLoading(false);
    setSelected(next);
    setRecommendations([]);
    setGenerated(false);
    setError("");
  }
  async function generate() {
    pending.current?.abort();
    const controller = new AbortController();
    pending.current = controller;
    setLoading(true);
    setError("");
    try {
      const data = await recommendMovies(
        selected.map((movie) => movie.id),
        AbortSignal.any([controller.signal, AbortSignal.timeout(15000)]),
        mediaType,
      );
      if (!controller.signal.aborted) {
        setRecommendations(data.recommendations);
        setGenerated(true);
      }
    } catch (err) {
      if (!controller.signal.aborted)
        setError(
          err instanceof Error
            ? err.message
            : "Something went wrong. Please try again.",
        );
    } finally {
      if (!controller.signal.aborted) setLoading(false);
    }
  }
  return (
    <>
      <section className="taste-section" aria-labelledby="taste-title">
        <div className="section-heading">
          <span>01</span>
          <h2 id="taste-title">Build your taste</h2>
        </div>
        <div className="taste-controls">
          <div className="search-row">
            <MovieSearch
              selected={selected}
              onSelect={(movie) => {
                if (
                  selected.length < 5 &&
                  !selected.some((item) => item.id === movie.id)
                )
                  changeSelection([...selected, movie]);
              }}
            />
            <button
              className="primary-button"
              disabled={!selected.length || loading}
              onClick={generate}
            >
              {loading ? (
                <>
                  <LoaderCircle size={18} className="spin" /> Finding your
                  titles…
                </>
              ) : (
                <>
                  Find My Next Watch <ArrowRight size={18} />
                </>
              )}
            </button>
          </div>
          <div className="selected-movies">
            <span className="taste-label">
              Your Taste <small>{selected.length}/5</small>
            </span>
            {selected.map((movie) => (
              <button
                className="taste-chip"
                key={movie.id}
                aria-label={`Remove ${movie.title}`}
                onClick={() =>
                  changeSelection(
                    selected.filter((item) => item.id !== movie.id),
                  )
                }
              >
                {movie.title}{" "}
                <small>
                  {movie.media_type === "series" ? "Series" : "Movie"}
                </small>
                <X size={14} />
              </button>
            ))}
            {!selected.length && (
              <span className="selection-hint">
                Start with one favorite. Three to five gives us a fuller
                picture.
              </span>
            )}
          </div>
          <div
            className="media-filter"
            role="group"
            aria-label="Recommendation type"
          >
            <span>Recommend:</span>
            {(
              [
                ["all", "Movies & series"],
                ["movie", "Movies"],
                ["series", "Series"],
              ] as const
            ).map(([value, label]) => (
              <button
                key={value}
                aria-pressed={mediaType === value}
                onClick={() => {
                  setMediaType(value);
                  changeSelection(selected);
                }}
              >
                {label}
              </button>
            ))}
          </div>
          <p className="sr-only" role="status">
            {selected.length} titles selected.
          </p>
          {error && (
            <p role="alert" className="error-message">
              {error}
            </p>
          )}
        </div>
      </section>
      <section
        className="results-section"
        aria-labelledby="results-title"
        aria-busy={loading}
      >
        <div className="results-heading">
          <div className="section-heading">
            <span>02</span>
            <h2 id="results-title">
              {generated ? "Recommended for you" : "Your next great watch"}
            </h2>
          </div>
          {generated && (
            <p>{recommendations.length} discoveries · Ranked by your taste</p>
          )}
        </div>
        {loading ? (
          <div className="empty-state" role="status">
            <LoaderCircle size={38} className="spin" />
            <h3>Connecting your favorites…</h3>
            <p>Comparing your taste with movies and series.</p>
          </div>
        ) : generated ? (
          <>
            <p className="score-note">
              Match is content similarity, not a rating or a prediction of
              enjoyment. Artwork is illustrative when a poster is unavailable.
            </p>
            <div className="movie-grid">
              {recommendations.map((movie, index) => (
                <MovieCard key={movie.id} movie={movie} index={index} />
              ))}
            </div>
            {!recommendations.length && (
              <p className="empty-state">
                No overlapping features found. Try adding another favorite.
              </p>
            )}
          </>
        ) : (
          <div className="empty-state">
            <Clapperboard size={47} strokeWidth={1.2} />
            <h3>Great watching starts with your taste.</h3>
            <p>Choose a few favorites above to discover what comes next.</p>
          </div>
        )}
      </section>
    </>
  );
}
