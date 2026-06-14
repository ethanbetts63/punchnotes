"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";

type Props = {
  page: number;
  totalPages: number;
};

function getPageNums(current: number, total: number): (number | "…")[] {
  if (total <= 9) return Array.from({ length: total }, (_, i) => i + 1);
  const nums: (number | "…")[] = [1];
  let start = Math.max(2, current - 2);
  let end = Math.min(total - 1, current + 2);

  if (current <= 3) {
    start = 2;
    end = 5;
  } else if (current >= total - 2) {
    start = total - 4;
    end = total - 1;
  }
  if (start > 2) nums.push("…");
  for (let i = start; i <= end; i++) nums.push(i);
  if (end < total - 1) nums.push("…");
  nums.push(total);
  return nums;
}

export default function Paginator({ page, totalPages }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  if (totalPages <= 1) return null;

  const btn = "flex h-8 min-w-[2rem] items-center justify-center rounded-lg border px-2 text-sm font-medium transition-colors";

  function goToPage(nextPage: number) {
    if (nextPage === page || nextPage < 1 || nextPage > totalPages) return;
    const params = new URLSearchParams(searchParams.toString());
    if (nextPage === 1) params.delete("page");
    else params.set("page", String(nextPage));
    const qs = params.toString();
    router.push(`${pathname}${qs ? `?${qs}` : ""}`, { scroll: false });
    window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
  }

  return (
    <div className="mt-6 flex items-center justify-center gap-1.5">
      <button
        onClick={() => goToPage(page - 1)}
        disabled={page === 1}
        className={`${btn} border-stone-200 text-stone-500 hover:border-stone-400 disabled:cursor-not-allowed disabled:opacity-40`}
      >
        ←
      </button>
      {getPageNums(page, totalPages).map((p, i) =>
        p === "…" ? (
          <span key={`el-${i}`} className="px-1 text-sm text-stone-300">…</span>
        ) : (
          <button
            key={p}
            onClick={() => goToPage(p)}
            className={`${btn} ${
              p === page
                ? "border-stone-900 bg-stone-900 text-white"
                : "border-stone-200 text-stone-600 hover:border-stone-400"
            }`}
          >
            {p}
          </button>
        )
      )}
      <button
        onClick={() => goToPage(page + 1)}
        disabled={page === totalPages}
        className={`${btn} border-stone-200 text-stone-500 hover:border-stone-400 disabled:cursor-not-allowed disabled:opacity-40`}
      >
        →
      </button>
    </div>
  );
}
