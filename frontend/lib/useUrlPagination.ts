"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

function pageFromParam(value: string | null): number {
  const parsed = Number(value);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1;
}

export function useUrlPagination(totalItems: number, pageSize: number) {
  const pathname = usePathname();
  const router = useRouter();
  const searchParams = useSearchParams();
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const page = Math.min(pageFromParam(searchParams.get("page")), totalPages);

  function setPage(nextPage: number) {
    const pageNumber = Math.min(Math.max(nextPage, 1), totalPages);
    const params = new URLSearchParams(searchParams.toString());

    if (pageNumber === 1) {
      params.delete("page");
    } else {
      params.set("page", String(pageNumber));
    }

    const qs = params.toString();
    router.push(`${pathname}${qs ? `?${qs}` : ""}`, { scroll: false });
  }

  return { page, totalPages, setPage };
}
