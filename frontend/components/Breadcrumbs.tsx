import Link from "next/link";
import { ChevronRight } from "lucide-react";

type BreadcrumbItem = {
  label: string;
  href?: string;
};

type Props = {
  items: BreadcrumbItem[];
  tone?: "light" | "dark";
  className?: string;
};

export default function Breadcrumbs({ items, tone = "light", className = "" }: Props) {
  const linkClass =
    tone === "dark"
      ? "text-stone-400 hover:text-white"
      : "text-stone-500 hover:text-stone-950";
  const currentClass = tone === "dark" ? "text-stone-200" : "text-stone-900";
  const separatorClass = tone === "dark" ? "text-stone-700" : "text-stone-300";

  return (
    <nav aria-label="Breadcrumb" className={`text-xs font-medium ${className}`}>
      <ol className="flex min-w-0 flex-wrap items-center gap-1.5">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;

          return (
            <li key={`${item.label}-${index}`} className="flex min-w-0 items-center gap-1.5">
              {item.href && !isLast ? (
                <Link href={item.href} className={`transition-colors ${linkClass}`}>
                  {item.label}
                </Link>
              ) : (
                <span className={`truncate ${isLast ? currentClass : linkClass}`} aria-current={isLast ? "page" : undefined}>
                  {item.label}
                </span>
              )}
              {!isLast && <ChevronRight className={`h-3 w-3 shrink-0 ${separatorClass}`} aria-hidden="true" />}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
