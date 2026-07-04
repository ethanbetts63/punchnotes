import Link from "next/link";
import type { ReactNode } from "react";
import ListPageSearchBar from "@/components/ListPageSearchBar";

type Props = {
  backHref?: string;
  backLabel?: string;
  title: string;
  subtitle?: string;
  searchPlaceholder: string;
  searchPath?: string;
  urlState?: boolean;
  controls?: ReactNode;
};

export default function ListPageHeader({
  backHref,
  backLabel,
  title,
  subtitle,
  searchPlaceholder,
  searchPath,
  urlState = true,
  controls,
}: Props) {
  return (
    <>
      {backHref && backLabel && (
        <Link
          href={backHref}
          className="mb-6 inline-flex items-center gap-1.5 text-sm font-medium text-stone-500 transition-colors hover:text-stone-900"
        >
          {`<- ${backLabel}`}
        </Link>
      )}

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-stone-900">{title}</h1>
        {subtitle && <p className="mt-2 text-stone-500">{subtitle}</p>}
      </div>

      <ListPageSearchBar placeholder={searchPlaceholder} searchPath={searchPath} urlState={urlState} />

      {controls}
    </>
  );
}
