"use client";

import Link from "next/link";
import Image from "next/image";
import { Search, X, Menu } from "lucide-react";
import { FormEvent, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

const navLinks = [
  { href: "/killtony", label: "Kill Tony" },
  { href: "/killtony/episodes", label: "Episodes" },
  { href: "/killtony/comedians", label: "Comedians" },
  { href: "/killtony/sets", label: "Sets" },
  { href: "/killtony/jokes", label: "Jokes" },
  { href: "/joke-originality-checker", label: "Originality" },
  // { href: "/articles", label: "Articles" },
  { href: "/about", label: "About" },
];

export default function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmed = query.trim();
    if (!trimmed) return;
    router.push(`/killtony/search?q=${encodeURIComponent(trimmed)}`);
    setSearchOpen(false);
    setQuery("");
  }

  function isActive(href: string) {
    return pathname === href || (href !== "/" && pathname.startsWith(href + "/"));
  }

  return (
    <header className="sticky top-0 z-50 bg-stone-950 border-b border-stone-800">

      {/* Main bar */}
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-4 px-4 sm:px-6">

        {/* Wordmark */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0 group">
          <div className="h-12 w-12 shrink-0 overflow-hidden rounded-full opacity-90 group-hover:opacity-100 transition-opacity">
            <Image
              src="/logo.png"
              alt="PunchNotes logo"
              width={48}
              height={48}
              className="object-cover w-full h-full"
            />
          </div>
          <span className="text-lg leading-none tracking-tight">
            <span className="font-black text-white">Punch</span><span className="font-black text-primary">Notes</span>
          </span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-0.5 ml-4">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                isActive(href)
                  ? "bg-primary/15 text-white"
                  : "text-stone-400 hover:text-stone-200 hover:bg-white/5"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>

        <div className="flex-1" />

        {/* Desktop search */}
        <form
          onSubmit={submitSearch}
          className="hidden md:flex items-center gap-2 min-w-44 max-w-xs w-full rounded-md border border-stone-700 bg-stone-900 px-3 py-1.5 transition-colors focus-within:border-stone-500"
        >
          <Search className="h-3.5 w-3.5 shrink-0 text-stone-500" aria-hidden="true" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Kill Tony…"
            className="min-w-0 flex-1 bg-transparent text-sm text-white placeholder:text-stone-500 focus:outline-none"
          />
        </form>

        {/* Mobile controls */}
        <div className="flex md:hidden items-center gap-2 ml-auto">
          <button
            onClick={() => { setSearchOpen(!searchOpen); setMenuOpen(false); }}
            className="p-1.5 text-stone-400 hover:text-white transition-colors"
            aria-label="Search"
          >
            <Search className="h-5 w-5" />
          </button>
          <button
            onClick={() => { setMenuOpen(!menuOpen); setSearchOpen(false); }}
            className="p-1.5 text-stone-400 hover:text-white transition-colors"
            aria-label="Menu"
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

      </div>

      {/* Mobile search bar */}
      {searchOpen && (
        <div className="md:hidden border-t border-stone-800 px-4 py-3">
          <form onSubmit={submitSearch} className="flex items-center gap-2 rounded-md border border-stone-700 bg-stone-900 px-3 py-2">
            <Search className="h-4 w-4 shrink-0 text-stone-500" />
            <input
              autoFocus
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search Kill Tony…"
              className="min-w-0 flex-1 bg-transparent text-sm text-white placeholder:text-stone-500 focus:outline-none"
            />
          </form>
        </div>
      )}

      {/* Mobile nav menu */}
      {menuOpen && (
        <nav className="md:hidden border-t border-stone-800 px-4 py-3 flex flex-col gap-1">
          {navLinks.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              onClick={() => setMenuOpen(false)}
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                isActive(href)
                  ? "bg-primary/15 text-white"
                  : "text-stone-400 hover:text-white hover:bg-white/5"
              }`}
            >
              {label}
            </Link>
          ))}
        </nav>
      )}

    </header>
  );
}
