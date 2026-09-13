import type { Movie, Recommendation, MediaFilter } from "@/types/movie";
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...init,
    signal: init?.signal ?? AbortSignal.timeout(15000),
  });
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    throw new Error(
      typeof body?.detail === "string"
        ? body.detail
        : "Could not reach the movie service. Please try again.",
    );
  }
  return response.json();
}
export const searchMovies = (query: string, signal: AbortSignal) =>
  request<Movie[]>(`/titles/search?q=${encodeURIComponent(query)}`, { signal });
export const recommendMovies = (
  ids: number[],
  signal: AbortSignal,
  mediaType: MediaFilter = "all",
) =>
  request<{ recommendations: Recommendation[] }>("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ movie_ids: ids, limit: 10, media_type: mediaType }),
    signal,
  });
