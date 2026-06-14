import Link from "next/link";
import type { ReactNode } from "react";

type Stat = {
  label: string;
  value: ReactNode;
};

type Props = {
  href: string;
  image: ReactNode;
  eyebrow?: string;
  title: string;
  subtitle?: string;
  meta?: ReactNode;
  badges?: ReactNode;
  stats?: Stat[];
};

export default function SearchResultTile({
  href,
  image,
  eyebrow,
  title,
  subtitle,
  meta,
  badges,
  stats,
}: Props) {
  return (
    <Link
      href={href}
      className="group block h-full overflow-hidden rounded-lg border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
    >
      <div className="relative aspect-video w-full overflow-hidden bg-stone-100">
        {image}
        {badges && <div className="absolute left-2 top-2 flex flex-wrap gap-1">{badges}</div>}
      </div>

      <div className="p-3">
        {eyebrow && (
          <p className="text-[11px] font-bold uppercase tracking-wide text-primary">
            {eyebrow}
          </p>
        )}
        <p
          className={`truncate font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary${
            eyebrow ? " mt-1" : ""
          }`}
        >
          {title}
        </p>
        {subtitle && <p className="mt-1 truncate text-xs leading-snug text-stone-500">{subtitle}</p>}
        {meta && <div className="mt-2 text-xs leading-snug text-stone-500">{meta}</div>}
        {stats && stats.length > 0 && (
          <div className="mt-3 grid grid-cols-2 gap-1.5">
            {stats.map((stat) => (
              <div
                key={stat.label}
                className="rounded-md border border-stone-100 bg-stone-50 px-2 py-1.5"
              >
                <p className="truncate text-[10px] leading-tight text-stone-400">{stat.label}</p>
                <p className="mt-0.5 truncate text-xs font-semibold leading-tight text-stone-800">
                  {stat.value}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </Link>
  );
}
