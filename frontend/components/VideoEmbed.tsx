"use client";

import { useState } from "react";
import { fmtSeconds } from "@/lib/killTonyDisplay";

type Props = {
  youtubeId: string | undefined | null;
  startSeconds: number;
  className?: string;
};

export default function VideoEmbed({ youtubeId, startSeconds, className = "" }: Props) {
  const [loaded, setLoaded] = useState(false);
  if (!youtubeId) return null;

  const embedUrl = `https://www.youtube.com/embed/${youtubeId}?start=${Math.floor(startSeconds)}&autoplay=1&rel=0`;

  if (loaded) {
    return (
      <div className={`relative w-full overflow-hidden rounded-xl bg-black ${className}`} style={{ aspectRatio: "16/9" }}>
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
      className={`group relative w-full overflow-hidden rounded-xl bg-black ${className}`}
      style={{ aspectRatio: "16/9" }}
      aria-label="Play video"
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={`https://img.youtube.com/vi/${youtubeId}/hqdefault.jpg`}
        alt="Episode thumbnail"
        className="absolute inset-0 h-full w-full object-cover opacity-80 transition-opacity group-hover:opacity-60"
      />
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="flex h-16 w-16 items-center justify-center rounded-full bg-white/90 shadow-lg transition-colors group-hover:bg-white">
          <svg className="ml-1 h-7 w-7 text-stone-900" fill="currentColor" viewBox="0 0 24 24">
            <path d="M8 5v14l11-7z" />
          </svg>
        </div>
      </div>
      {startSeconds > 0 && (
        <div className="absolute bottom-3 left-3 rounded-md bg-black/70 px-2.5 py-1 text-xs font-medium text-white tabular-nums">
          Starts at {fmtSeconds(startSeconds)}
        </div>
      )}
    </button>
  );
}
