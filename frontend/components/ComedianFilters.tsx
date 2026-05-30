"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";

const ATTRIBUTE_OPTIONS = [
  { value: "", label: "All types" },
  { value: "bucket_pull", label: "Bucket Pull" },
  { value: "regular", label: "Regular" },
  { value: "golden_ticket", label: "Golden Ticket" },
  { value: "special", label: "Special" },
];

const JOKE_BOOK_OPTIONS = [
  { value: "small", label: "Small Joke Book" },
  { value: "medium", label: "Medium Joke Book" },
  { value: "large", label: "Large Joke Book" },
];

export default function ComedianFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const currentAttribute = sp.get("attribute") ?? "";
  const currentJokeBook = sp.get("joke_book") ?? "";

  function navigate(attribute: string, jokeBook: string) {
    const params = new URLSearchParams();
    const q = sp.get("q");
    if (q) params.set("q", q);
    if (attribute) params.set("attribute", attribute);
    if (jokeBook) params.set("joke_book", jokeBook);
    const qs = params.toString();
    router.push(`${pathname}${qs ? `?${qs}` : ""}`);
  }

  const chip = (active: boolean) =>
    `rounded-full border px-3 py-1 text-xs font-medium transition-colors ${
      active
        ? "border-stone-900 bg-stone-900 text-white"
        : "border-stone-200 bg-white text-stone-600 hover:border-stone-400"
    }`;

  return (
    <div className="mb-6 space-y-3">
      <div className="flex flex-wrap gap-2">
        {ATTRIBUTE_OPTIONS.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => navigate(value, currentJokeBook)}
            className={chip(currentAttribute === value)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="flex flex-wrap gap-2">
        {JOKE_BOOK_OPTIONS.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => navigate(currentAttribute, currentJokeBook === value ? "" : value)}
            className={chip(currentJokeBook === value)}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
