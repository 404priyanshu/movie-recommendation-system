"use client";
import Image from "next/image";
import { useState } from "react";
import type { CSSProperties } from "react";
import { ChevronDown } from "lucide-react";
import type { Recommendation } from "@/types/movie";
export default function MovieCard({
  movie,
  index,
}: {
  movie: Recommendation;
  index: number;
}) {
  const [imageFailed, setImageFailed] = useState(false);
  return (
    <article className="movie-card" style={{ "--i": index } as CSSProperties}>
      <div className={`poster art-${index % 3}`}>
        {movie.poster_url && !imageFailed ? (
          <Image
            unoptimized
            fill
            sizes="(max-width: 650px) 45vw, 20vw"
            src={movie.poster_url}
            alt={`${movie.title} poster`}
            loading="lazy"
            onError={() => setImageFailed(true)}
          />
        ) : (
          <div className="poster-type">
            <span>CINEMATCH COLLECTION</span>
            <strong>{movie.title}</strong>
            <small>Genre artwork · {movie.year ?? "Undated"}</small>
          </div>
        )}
        <span
          className="match"
          title="Ranking score: 85% story and genre similarity, 10% popularity, 5% recency. Not a probability of enjoyment."
        >
          {(movie.score * 100).toFixed(1)} ranking score
        </span>
      </div>
      <div className="movie-meta">
        <span>{String(index + 1).padStart(2, "0")}</span>
        <span>
          {movie.media_type === "series" ? "Series" : "Movie"} ·{" "}
          {movie.year ?? "Year unknown"}
        </span>
      </div>
      <h3>{movie.title}</h3>
      <p className="genres">
        {movie.genres.join(" · ") || "Genres unavailable"}
      </p>
      {(movie.platforms?.length ?? 0) > 0 && (
        <p className="platforms">
          Streaming on {movie.platforms.join(", ")}
        </p>
      )}
      <p className="description">
        {movie.overview ||
          "No synopsis available. Discover this title through the tastes you share."}
      </p>
      {movie.source_url && (
        <a
          className="source-link"
          href={movie.source_url}
          target="_blank"
          rel="noreferrer"
        >
          View on TMDB ↗
        </a>
      )}
      <p className="reason">{movie.explanation}</p>
      <details>
        <summary>
          Why this title? <ChevronDown size={15} />
        </summary>
        <div className="explanation">
          <p>Based on: {movie.selected_titles.join(", ")}.</p>
          <ul>
            {movie.reasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
          <p>Top shared story and genre terms contributing to the content score ({(movie.content_score * 100).toFixed(1)}%):</p>
          {movie.shared_features.map((feature) => (
            <div className="feature" key={feature.term}>
              <span>{feature.term}</span>
              <span>{feature.contribution.toFixed(4)}</span>
            </div>
          ))}
          <small>
            Contributions across all terms sum to the cosine score. Shown here:
            up to six strongest terms.
          </small>
        </div>
      </details>
    </article>
  );
}
