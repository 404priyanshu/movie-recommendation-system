import Discovery from "@/components/discovery";

export default function Home() {
  return (
    <main id="main">
      {/* The one-sheet: title treatment, the action struck beneath it,
          then the billing slab carrying the real credits. */}
      <section className="sheet">
        <div className="sheet-copy">
          <h1>
            Ten titles.
            <em>Every reason shown.</em>
          </h1>
          <p className="sheet-lede">
            Name a few things you loved. CineMatch reads what they are made of
            and credits the ten it draws from them — with the terms, and the
            arithmetic, set beside each one.
          </p>
        </div>
        <div
          className="sheet-art"
          role="img"
          aria-label="Original cinematic illustrations of space, desert, and mountains"
        >
          <i />
          <i />
          <i />
        </div>
      </section>

      <div className="slab">
        <b>CineMatch</b>
        <span>A content-based recommender</span>
        <span className="gold">TF-IDF &amp; cosine similarity</span>
        <span>Catalog by TMDB</span>
        <span>Series data TVmaze CC BY-SA</span>
        <span>Match is content similarity — not a rating</span>
      </div>

      <Discovery />
    </main>
  );
}
