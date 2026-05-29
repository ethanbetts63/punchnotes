import Link from "next/link";

export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black/80 py-8">
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
          <p className="text-sm text-stone-500">
            <span className="font-semibold text-stone-400">PunchPedia</span> — comedy analytics
          </p>
          <nav className="flex gap-4 text-sm text-stone-500">
            <Link href="/killtony" className="hover:text-stone-300 transition-colors">Kill Tony</Link>
            <Link href="/about" className="hover:text-stone-300 transition-colors">About</Link>
          </nav>
        </div>
      </div>
    </footer>
  );
}
