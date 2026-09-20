"use client";
import { useRef, useState, useEffect } from "react";
import type { CSSProperties } from "react";
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
  const [leaving, setLeaving] = useState<number | null>(null);
  const pending = useRef<AbortController | null>(null);
  const exitTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(
    () => () => {
      pending.current?.abort();
      if (exitTimer.current) clearTimeout(exitTimer.current);
    },
    [],
  );
  function changeSelection(next: Movie[]) {
    pending.current?.abort();
    setLoading(false);
    setSelected(next);
    setRecommendations([]);
    setGenerated(false);
    setError("");
  }
  // Let the chip play its exit before it leaves the DOM; reduced-motion
  // users skip the wait entirely.
  function removeMovie(id: number) {
    if (leaving !== null) return;
    const instant =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const drop = () => {
      setLeaving(null);
      changeSelection(selected.filter((item) => item.id !== id));
    };
    if (instant) return drop();
    setLeaving(id);
    exitTimer.current = setTimeout(drop, 170);
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
      <section className="act" aria-labelledby="taste-title">
        <div className="act-head">
          <i>Act 01</i>
          <h2 id="taste-title">Credit your favourites</h2>
          <p>Up to five</p>
        </div>
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
                <LoaderCircle size={17} className="spin" /> Reading
              </>
            ) : (
              <>
                Roll credits <ArrowRight size={17} />
              </>
            )}
          </button>
        </div>
        <div className="cast">
          <span className="cast-label">
            Cast <b>{selected.length}</b>/5
          </span>
          {selected.map((movie) => (
            <button
              className={`taste-chip${leaving === movie.id ? " leaving" : ""}`}
              key={movie.id}
              aria-label={`Remove ${movie.title}`}
              onClick={() => removeMovie(movie.id)}
            >
              {movie.title}{" "}
              <small>{movie.media_type === "series" ? "Series" : "Movie"}</small>
              <X size={13} />
            </button>
          ))}
          {!selected.length && (
            <span className="selection-hint">
              Start with one. Three to five reads clearest.
            </span>
          )}
        </div>
        <div className="media-filter" role="group" aria-label="Recommendation type">
          <span>Bill:</span>
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
      </section>
      <section
        className="act credits"
        aria-labelledby="results-title"
        aria-busy={loading}
      >
        <div className="act-head">
          <i>Act 02</i>
          <h2 id="results-title">
            {generated ? "The billing" : "Your next great watch"}
          </h2>
          {generated && <p>{recommendations.length} credited · ranked by your taste</p>}
        </div>

        {loading ? (
          <>
            <p className="loading-note">
              <LoaderCircle size={14} className="spin" />
              Scoring the catalog against your cast
            </p>
            <div aria-hidden="true">
              {Array.from({ length: 6 }, (_, position) => (
                <div
                  className="skeleton-credit"
                  key={position}
                  style={{ "--i": position } as CSSProperties}
                >
                  <div className="skeleton-poster" />
                  <div className="skeleton-lines">
                    <div />
                    <div />
                    <div />
                    <div />
                  </div>
                </div>
              ))}
            </div>
            <p className="sr-only" role="status">
              Finding recommendations.
            </p>
          </>
        ) : generated ? (
          <>
            <p className="credit-note">
              Match is content similarity — not a rating, and not a prediction
              of enjoyment. Term size shows each term&rsquo;s share of the score.
              Artwork is illustrative when a poster is unavailable.
            </p>
            {recommendations.map((movie, index) => (
              <MovieCard key={movie.id} movie={movie} index={index} />
            ))}
            {!recommendations.length && (
              <div className="empty">
                <h3>No overlap found</h3>
                <p>Nothing in the catalog shares enough features with this cast. Try adding another title.</p>
              </div>
            )}
          </>
        ) : (
          <div className="empty">
            <Clapperboard size={40} strokeWidth={1.3} />
            <h3>The billing is empty</h3>
            <p>Credit a few favourites above and CineMatch will draw up the list.</p>
          </div>
        )}
      </section>
    </>
  );
}
