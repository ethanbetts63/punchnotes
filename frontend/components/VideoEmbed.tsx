"use client";

import { useEffect, useRef, useState } from "react";
import YouTube, { type YouTubePlayer, type YouTubeProps } from "react-youtube";
import { fmtSeconds } from "@/lib/killTonyDisplay";

type Props = {
  youtubeId: string | undefined | null;
  startSeconds: number;
  className?: string;
};

function isEditableTarget(target: EventTarget | null) {
  if (!(target instanceof HTMLElement)) return false;
  const tagName = target.tagName.toLowerCase();
  return (
    tagName === "input" ||
    tagName === "textarea" ||
    tagName === "select" ||
    target.isContentEditable
  );
}

export default function VideoEmbed({ youtubeId, startSeconds, className = "" }: Props) {
  const [loaded, setLoaded] = useState(false);
  const playerRef = useRef<YouTubePlayer | null>(null);

  useEffect(() => {
    if (!loaded) return;

    async function handleKeyDown(event: KeyboardEvent) {
      if (
        event.defaultPrevented ||
        event.altKey ||
        event.ctrlKey ||
        event.metaKey ||
        isEditableTarget(event.target)
      ) {
        return;
      }

      const delta = event.key === "ArrowLeft" ? -5 : event.key === "ArrowRight" ? 5 : 0;
      if (!delta || !playerRef.current) return;

      event.preventDefault();

      const [currentTime, duration] = await Promise.all([
        playerRef.current.getCurrentTime(),
        playerRef.current.getDuration(),
      ]);
      const nextTime = Math.max(
        0,
        duration > 0 ? Math.min(duration, currentTime + delta) : currentTime + delta,
      );
      playerRef.current.seekTo(nextTime, true);
    }

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [loaded]);

  if (!youtubeId) return null;

  const onReady: YouTubeProps["onReady"] = (event) => {
    playerRef.current = event.target;
  };

  const opts: YouTubeProps["opts"] = {
    playerVars: {
      autoplay: 1,
      rel: 0,
      start: Math.floor(startSeconds),
    },
  };

  if (loaded) {
    return (
      <div className={`relative w-full overflow-hidden rounded-none bg-black sm:rounded-xl ${className}`} style={{ aspectRatio: "16/9" }}>
        <YouTube
          videoId={youtubeId}
          opts={opts}
          onReady={onReady}
          className="absolute inset-0 h-full w-full"
          iframeClassName="h-full w-full"
          title="YouTube video player"
        />
      </div>
    );
  }

  return (
    <button
      onClick={() => setLoaded(true)}
      className={`group relative w-full overflow-hidden rounded-none bg-black sm:rounded-xl ${className}`}
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
