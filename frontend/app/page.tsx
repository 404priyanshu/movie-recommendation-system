import Discovery from "@/components/discovery";
export default function Home() {
  return (
    <main id="main">
      <section className="hero">
        <div className="hero-copy">
          <h1>Find your next favorite watch.</h1>
          <p>
            Pick a few movies and series you love and CineMatch will learn your
            taste.
          </p>
          <div className="hero-signature">
            <span />
            Different people. A brighter watchlist.
          </div>
        </div>
        <div
          className="hero-art"
          aria-label="Original cinematic illustrations of space, desert, and mountains"
          role="img"
        >
          <div className="art-panel art-0">
            <span>
              BIGGER
              <br />
              STORIES.
              <br />
              AWAIT.
            </span>
          </div>
          <div className="art-panel art-1">
            <span>
              NEW WORLDS.
              <br />
              NEW PERSPECTIVE.
            </span>
          </div>
          <div className="art-panel art-2">
            <span>
              GREAT MOVIES
              <br />
              TAKE YOU
              <br />
              FURTHER.
            </span>
          </div>
        </div>
      </section>
      <Discovery />
    </main>
  );
}
