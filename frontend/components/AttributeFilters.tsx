"use client";

import { useRouter, useSearchParams, usePathname } from "next/navigation";

const ATTRIBUTE_OPTIONS = [
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

export default function AttributeFilters() {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const currentAttribute = sp.get("attribute") ?? "";
  const currentJokeBook = sp.get("joke_book") ?? "";
  const currentQ = sp.get("q") ?? "";
  const isListMode = !!(currentQ || currentAttribute || currentJokeBook || sp.get("view"));

  function navigateListView() {
    const params = new URLSearchParams();
    if (currentQ) params.set("q", currentQ);
    params.set("view", "list");
    router.push(`${pathname}?${params.toString()}`);
  }

  function navigateAttribute(attribute: string) {
    const params = new URLSearchParams();
    if (currentQ) params.set("q", currentQ);
    if (currentJokeBook) params.set("joke_book", currentJokeBook);
    if (attribute) params.set("attribute", attribute);
    router.push(`${pathname}?${params.toString()}`);
  }

  function navigateJokeBook(jokeBook: string) {
    const params = new URLSearchParams();
    if (currentQ) params.set("q", currentQ);
    if (currentAttribute) params.set("attribute", currentAttribute);
    if (jokeBook) params.set("joke_book", jokeBook);
    if (!currentAttribute && !currentQ && !jokeBook) params.set("view", "list");
    router.push(`${pathname}?${params.toString()}`);
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
        <button onClick={navigateListView} className={chip(!currentAttribute && isListMode)}>
          List view
        </button>
        {ATTRIBUTE_OPTIONS.map(({ value, label }) => (
          <button
            key={value}
            onClick={() => navigateAttribute(value)}
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
            onClick={() => navigateJokeBook(currentJokeBook === value ? "" : value)}
            className={chip(currentJokeBook === value)}
          >
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
