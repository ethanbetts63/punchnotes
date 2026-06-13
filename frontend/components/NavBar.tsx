"use client";

import Link from "next/link";
import { Search } from "lucide-react";
import { FormEvent, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

const navLinks = [
  { href: "/killtony", label: "Kill Tony" },
  { href: "/killtony/episodes", label: "Episodes" },
  { href: "/killtony/comedians", label: "Comedians" },
  { href: "/killtony/sets", label: "Sets" },
  { href: "/killtony/jokes", label: "Jokes" },
  { href: "/articles", label: "Articles" },
  { href: "/about", label: "About" },
];

export default function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [query, setQuery] = useState("");

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    router.push(`/killtony/search?q=${encodeURIComponent(trimmed)}`);
  }

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-black/80 backdrop-blur-sm">
      <div className="mx-auto flex h-14 max-w-7xl items-center gap-6 px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-1.5 shrink-0">
          <span className="text-lg font-bold text-white tracking-tight">
            Punch<span className="text-primary">Notes</span>
          </span>
        </Link>

        <form
          onSubmit={submitSearch}
          className="hidden min-w-44 max-w-sm flex-1 items-center gap-2 rounded-md border border-white/10 bg-white/5 px-2.5 py-1.5 transition-colors focus-within:border-white/25 md:flex"
        >
          <Search className="h-3.5 w-3.5 shrink-0 text-stone-500" aria-hidden="true" />
          <input
            type="text"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search Kill Tony"
            className="min-w-0 flex-1 bg-transparent text-sm text-white placeholder:text-stone-500 focus:outline-none"
          />
        </form>

        <nav className="flex items-center gap-1 overflow-x-auto">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`whitespace-nowrap rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${pathname === href || pathname.startsWith(href + "/") ? "bg-white/10 text-white" : "text-stone-400 hover:text-white hover:bg-white/5"}`}
            >
              {label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
