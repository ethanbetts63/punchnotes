import Link from "next/link";
import type { TileData } from "@/lib/tiles";

function HighlightBody({ text, query }: { text: string; query: string }) {
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const parts = text.split(new RegExp(`(${escaped})`, "ig"));
  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase()
          ? <span key={i} className="font-black text-stone-950">{part}</span>
          : part
      )}
    </>
  );
}

export default function MediaTile({ item }: { item: TileData }) {
  if (item.variant === "joke") {
    return (
      <Link
        href={item.href}
        className="group flex h-full flex-col rounded-lg border border-stone-200 bg-white p-4 transition-all hover:shadow-md"
      >
        <div className="flex items-start justify-between gap-2">
          <p className="text-sm font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary">
            {item.title}
          </p>
          {item.badges && item.badges.length > 0 && (
            <span className={`shrink-0 inline-flex rounded-full px-2 py-0.5 text-[10px] font-bold ${item.badges[0].className}`}>
              {item.badges[0].label}
            </span>
          )}
        </div>
        {(item.bodyHighlight || item.body) && (
          <p className="mt-5 text-base leading-snug text-stone-700">
            &ldquo;
            {item.bodyQuery ? (
              <HighlightBody text={item.body ?? item.bodyHighlight ?? ""} query={item.bodyQuery} />
            ) : (
              <>
                {item.bodyPrefix}
                <span className="font-black text-stone-950">{item.bodyHighlight ?? item.body}</span>
              </>
            )}
            &rdquo;
          </p>
        )}
        {item.meta && (
          <p className="mt-auto line-clamp-3 pt-4 text-xs leading-snug text-stone-500">
            {item.meta}
          </p>
        )}
      </Link>
    );
  }

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
            className="absolute inset-0 h-full w-full object-contain"
          />
        ) : item.videoId ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={`https://img.youtube.com/vi/${item.videoId}/mqdefault.jpg`}
            alt={item.title}
            loading="lazy"
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
          <div className="absolute top-2 left-2 flex flex-wrap gap-1">
            {item.badges.map((b) => (
              <span key={b.label} className={`rounded-full px-2 py-0.5 text-[10px] font-bold ${b.className}`}>
                {b.label}
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
