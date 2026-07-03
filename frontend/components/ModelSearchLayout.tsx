import { Suspense } from "react";
import { Loader2 } from "lucide-react";
import ListPageHeader from "@/components/ListPageHeader";

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

function ResultsLoading() {
  return (
    <div className="flex items-center justify-center py-24">
      <Loader2 className="h-8 w-8 animate-spin text-stone-400" />
    </div>
  );
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
        <Suspense>
          <ListPageHeader
            backHref={backHref}
            backLabel={backLabel}
            title={title}
            searchPlaceholder={searchPlaceholder}
            controls={controls}
          />
        </Suspense>

        <Suspense fallback={<ResultsLoading />}>{children}</Suspense>
      </div>
    </div>
  );
}
