import type { ReactNode } from "react";
import ListPageSearchBar from "@/components/ListPageSearchBar";

type Props = {
  title: string;
  subtitle?: string;
  searchPlaceholder: string;
  searchPath?: string;
  controls?: ReactNode;
};

export default function ListPageHeader({ title, subtitle, searchPlaceholder, searchPath, controls }: Props) {
  return (
    <>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-stone-900">{title}</h1>
        {subtitle && <p className="mt-2 text-stone-500">{subtitle}</p>}
      </div>

      <ListPageSearchBar placeholder={searchPlaceholder} searchPath={searchPath} />

      {controls}
    </>
  );
}
