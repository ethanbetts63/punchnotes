import { Suspense } from "react";
import ListPageHeader from "@/components/ListPageHeader";

type Props = {
  title: string;
  backHref?: string;
  backLabel?: string;
  searchPlaceholder: string;
  subtitle: string;
  controls: React.ReactNode;
  emptyMessage: string;
  isEmpty: boolean;
  children: React.ReactNode;
};

export function buildSearchSubtitle(count: number | null, singular: string, plural: string, query: string): string {
  if (count == null) return "Loading...";
  return `${count} ${count === 1 ? singular : plural}${query ? ` matching "${query}"` : ""}`;
}

export default function ModelSearchLayout({
  title,
  backHref,
  backLabel,
  searchPlaceholder,
  subtitle,
  controls,
  emptyMessage,
  isEmpty,
  children,
}: Props) {
  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <Suspense>
          <ListPageHeader
            backHref={backHref}
            backLabel={backLabel}
            title={title}
            subtitle={subtitle}
            searchPlaceholder={searchPlaceholder}
            controls={controls}
          />
        </Suspense>

        {isEmpty ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">{emptyMessage}</p>
          </div>
        ) : (
          <Suspense>{children}</Suspense>
        )}
      </div>
    </div>
  );
}
