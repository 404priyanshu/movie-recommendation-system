import Link from "next/link";
import { ArrowRight } from "lucide-react";
const steps = [
  [
    "Movie & series metadata",
    "We combine MovieLens movies with a cached TVmaze series catalog using titles and genres. TVmaze Science-Fiction maps to Sci-Fi so both sources share a feature. Every movie has a stable ID. Ratings are not used in this version, and optional TMDB posters and synopses are display information only.",
  ],
  [
    "Text preparation",
    "Remove the release year from the title, lowercase text, and clean punctuation. Drop IMAX because it is a format, not story content. Sci-Fi becomes scifi, so it stays one feature. We repeat each genre three times to give genre overlap more influence than incidental title words.",
  ],
  [
    "TF-IDF vectorization",
    "The vectorizer learns a vocabulary from the whole catalog. Each movie becomes a row of numbers, with one column for each term. Common terms get lower inverse-document-frequency weights; distinctive ones get higher weights. Rows are normalized to length one.",
  ],
  [
    "Your taste vector",
    "Choose up to five favorites. We average their vectors so each movie has an equal vote. A term that appears across your favorites tends to have a larger value in this profile.",
  ],
  [
    "Cosine similarity",
    "Compare the direction of the taste vector to each movie vector. A score near one means they point in a similar direction. Zero means they share no weighted terms. A match percentage is this score multiplied by 100, not a probability that you will like the movie.",
  ],
  [
    "Top recommendations",
    "Exclude your selected movies, sort scores from highest to lowest, and return up to ten positive matches. Ties are resolved by movie ID. The explanation lists overlapping genres and the actual term contributions to your score.",
  ],
];
export default function HowItWorks() {
  return (
    <main id="main" className="learn-page">
      <h1>
        A little movie science.
        <br />A lot more discovery.
      </h1>
      <p className="learn-intro">
        No mysterious movie oracle. Just the things you love, turned into
        numbers we can compare.
      </p>
      <div className="pipeline">
        {steps.map(([title, text], index) => (
          <section className="pipeline-step" key={title}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <div>
              <h2>{title}</h2>
              <p>{text}</p>
              {index < 5 && <span aria-hidden="true">↓</span>}
            </div>
          </section>
        ))}
      </div>
      <section className="vector-example">
        <h2>Two movies. Some common ground.</h2>
        <p>
          Movie A: “Sci-Fi Space Adventure”
          <br />
          Movie B: “Sci-Fi Space Drama”
        </p>
        <table>
          <caption className="sr-only">
            Simplified term counts before TF-IDF weighting
          </caption>
          <thead>
            <tr>
              <th>Movie</th>
              <th>scifi</th>
              <th>space</th>
              <th>adventure</th>
              <th>drama</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>A</td>
              <td>1</td>
              <td>1</td>
              <td>1</td>
              <td>0</td>
            </tr>
            <tr>
              <td>B</td>
              <td>1</td>
              <td>1</td>
              <td>0</td>
              <td>1</td>
            </tr>
          </tbody>
        </table>
        <p>
          These simplified count vectors share two terms. Their cosine
          similarity is 2 ÷ (√3 × √3) ≈ 0.667. The real application uses TF-IDF
          weights instead of these counts, so its scores will differ. “Space” is
          illustrative here; MovieLens has no plot descriptions in our model.
        </p>
      </section>
      <p className="learn-bottom">
        A thoughtful limitation: similar metadata does not guarantee a great
        movie night. This model cannot understand acting, tone, or your changing
        mood. It can also keep you in a similarity bubble. Try a favorite from a
        different genre to broaden your profile.
      </p>
      <Link className="primary-button mt-8 w-fit" href="/">
        Build your taste <ArrowRight size={17} />
      </Link>
      <p className="learn-bottom">
        Data:{" "}
        <a
          href="https://grouplens.org/datasets/movielens/latest/"
          className="underline"
        >
          GroupLens MovieLens
        </a>
        . Optional imagery and synopses: TMDB. This product uses the TMDB API
        but is not endorsed or certified by TMDB.
      </p>
    </main>
  );
}
