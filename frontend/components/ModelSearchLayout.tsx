import { Suspense } from "react";
import ListPageHeader from "@/components/ListPageHeader";
import { SearchTransitionProvider } from "@/components/SearchTransition";
import SearchResults, { ResultsLoading } from "@/components/SearchResults";

type Props = {
  title: string;
  backHref?: string;
  backLabel?: string;
  searchPlaceholder: string;
  controls: React.ReactNode;
  children: React.ReactNode;
};

export function buildSearchSubtitle(count: number, singular: string, plural: string, query: string): string {
  return `${count} ${count === 1 ? singular : plural}${query ? ` matching "${query}"` : ""}`;
}

export default function ModelSearchLayout({
  title,
  backHref,
  backLabel,
  searchPlaceholder,
  controls,
  children,
}: Props) {
  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <SearchTransitionProvider>
          <Suspense>
            <ListPageHeader
              backHref={backHref}
              backLabel={backLabel}
              title={title}
              searchPlaceholder={searchPlaceholder}
              controls={controls}
            />
          </Suspense>

          <Suspense fallback={<ResultsLoading />}>
            <SearchResults>{children}</SearchResults>
          </Suspense>
        </SearchTransitionProvider>
      </div>
    </div>
  );
}
