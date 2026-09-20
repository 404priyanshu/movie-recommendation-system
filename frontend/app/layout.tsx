import type { Metadata } from "next";
import { Bodoni_Moda, Instrument_Sans } from "next/font/google";
import Link from "next/link";
import { Film, ArrowUpRight } from "lucide-react";
import "./globals.css";

// Display: a high-contrast didone for the masthead and titles.
// UI: a plain grotesque for controls, labels and data.
const display = Bodoni_Moda({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});
const sans = Instrument_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});
export const metadata: Metadata = {
  title: "CineMatch — Find your next favorite watch",
  description:
    "A thoughtful movie discovery experience powered by explainable content-based recommendations.",
};
export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${display.variable} ${sans.variable}`}>
      <body>
        <a href="#main" className="skip-link">
          Skip to content
        </a>
        <header className="site-header">
          <Link href="/" className="brand">
            <Film size={27} />
            <span>CineMatch</span>
          </Link>
          <nav aria-label="Main navigation">
            <Link href="/">Discover</Link>
            <Link href="/how-it-works">
              How it works <ArrowUpRight size={14} />
            </Link>
          </nav>
        </header>
        {children}
        <footer>
          <Link href="/" className="footer-brand">
            CineMatch
          </Link>
          <span>
            Content-based recommendations · TF-IDF & cosine similarity
          </span>
          <a href="https://www.tvmaze.com/api#licensing">
            Series data: TVmaze · CC BY-SA
          </a>
        </footer>
      </body>
    </html>
  );
}
