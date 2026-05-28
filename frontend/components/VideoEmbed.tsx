"use client";

import { useState } from "react";

function fmtSeconds(s: number): string {
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = Math.floor(s % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
  return `${m}:${String(sec).padStart(2, "0")}`;
}

function extractVideoId(url: string | undefined | null): string | null {
  if (!url) return null;
  const m = url.match(/[?&]v=([^&]+)/);
  return m ? m[1] : null;
}

type Props = {
  episodeUrl: string | undefined | null;
  startSeconds: number;
};

export default function VideoEmbed({ episodeUrl, startSeconds }: Props) {
  const [loaded, setLoaded] = useState(false);
  const videoId = extractVideoId(episodeUrl);
  if (!videoId) return null;

  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
  const embedUrl = `https://www.youtube.com/embed/${videoId}?start=${Math.floor(startSeconds)}&autoplay=1&rel=0`;

  if (loaded) {
    return (
      <div className="relative w-full overflow-hidden rounded-xl bg-black" style={{ aspectRatio: "16/9" }}>
        <iframe
          src={embedUrl}
          className="absolute inset-0 h-full w-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    );
  }

  return (
    <button
      onClick={() => setLoaded(true)}
      className="group relative w-full overflow-hidden rounded-xl bg-black"
      style={{ aspectRatio: "16/9" }}
      aria-label="Play video"
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={thumbnailUrl}
        alt="Episode thumbnail"
        className="absolute inset-0 h-full w-full object-cover opacity-80 group-hover:opacity-60 transition-opacity"
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg group-hover:bg-white transition-colors">
          <svg className="ml-1 h-7 w-7 text-stone-900" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
      </div>
      <div className="absolute bottom-3 left-3 rounded-md bg-black/70 px-2.5 py-1 text-xs font-medium text-white tabular-nums">
        Starts at {fmtSeconds(startSeconds)}
      </div>
    </button>
  );
}
