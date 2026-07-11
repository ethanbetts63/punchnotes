import Link from "next/link";
import type { TileData } from "@/lib/tiles";

export default function MediaTile({ item }: { item: TileData }) {
  return (
    <Link
      href={item.href}
      className="group block h-full overflow-hidden rounded-lg border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
    >
      <div className="relative aspect-video w-full overflow-hidden bg-stone-100">
        {item.imageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={item.imageUrl}
            alt={item.title}
            loading="lazy"
            decoding="async"
            className="absolute inset-0 h-full w-full object-contain"
          />
        ) : item.videoId ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`https://img.youtube.com/vi/${item.videoId}/mqdefault.jpg`}
            alt={item.title}
            loading="lazy"
            decoding="async"
            className="absolute inset-0 h-full w-full object-contain"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <svg className="h-8 w-8 text-stone-300" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
          </div>
        )}

        {item.badges && item.badges.length > 0 && (
          <div className="absolute bottom-2 right-2 flex flex-wrap justify-end gap-1">
            {item.badges.map((badge) => (
              <span key={badge.label} className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${badge.className}`}>
                {badge.label}
              </span>
            ))}
          </div>
        )}
      </div>

      <div className="p-2.5">
        {item.eyebrow && (
          <p className="text-[11px] font-bold uppercase tracking-wide text-primary">{item.eyebrow}</p>
        )}
        <p className={`truncate font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary${item.eyebrow ? " mt-1" : ""}`}>
          {item.title}
        </p>
        {item.meta && (
          <p className="mt-1 text-xs leading-snug text-stone-500">{item.meta}</p>
        )}
      </div>
    </Link>
  );
}
