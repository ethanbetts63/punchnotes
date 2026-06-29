import Link from "next/link";
import Image from "next/image";

const LABEL_CLASS = "text-[10px] font-bold uppercase tracking-[0.25em] text-primary mb-4";
const LINK_CLASS = "text-sm text-stone-400 hover:text-stone-200 transition-colors duration-200";

export default function Footer() {
  return (
    <footer className="bg-stone-950">
      <div className="mx-auto max-w-6xl px-6 py-12 grid grid-cols-1 md:grid-cols-3 gap-10">

        {/* Brand */}
        <div>
          <div className="flex items-center gap-2.5 mb-4">
            <div className="h-11 w-11 shrink-0 overflow-hidden rounded-full">
              <Image src="/logo.png" alt="PunchNotes logo" width={44} height={44} className="object-cover w-full h-full" />
            </div>
            <p className={LABEL_CLASS} style={{ marginBottom: 0 }}>PunchNotes</p>
          </div>
          <p className="text-sm text-stone-400 leading-relaxed">
            Structured comedy analytics for Kill Tony. Sets, comedians, and jokes broken
            down by premise, mechanism, and audience response.
          </p>
          <p className="mt-4 text-sm text-stone-400">
            <a href="mailto:ethanbetts63@gmail.com" className="hover:text-stone-200 transition-colors duration-200">
              ethanbetts63@gmail.com
            </a>
          </p>
          <p className="mt-4 text-xs text-stone-600 leading-relaxed">
            Fan-made archive. Not affiliated with Kill Tony, Tony Hinchcliffe, or any
            official channel.
          </p>
        </div>

        {/* Kill Tony */}
        <div>
          <p className={LABEL_CLASS}>Kill Tony</p>
          <ul className="space-y-2">
            <li><Link href="/killtony" className={LINK_CLASS}>Hub</Link></li>
            <li><Link href="/killtony/episodes" className={LINK_CLASS}>Episodes</Link></li>
            <li><Link href="/killtony/comedians" className={LINK_CLASS}>Comedians</Link></li>
            <li><Link href="/killtony/sets" className={LINK_CLASS}>Sets</Link></li>
            <li><Link href="/killtony/jokes" className={LINK_CLASS}>Jokes</Link></li>
          </ul>
        </div>

        {/* Site */}
        <div>
          <p className={LABEL_CLASS}>Site</p>
          <ul className="space-y-2 mb-6">
            <li><Link href="/about" className={LINK_CLASS}>About</Link></li>
          </ul>
          <p className="text-[10px] font-bold uppercase tracking-[0.25em] text-stone-600 mb-3">How sets are annotated</p>
          <div className="text-xs text-stone-600 space-y-1 leading-relaxed">
            <p>Each set is broken into <span className="text-stone-500">bits</span> (topic clusters), <span className="text-stone-500">beats</span> (individual jokes), and <span className="text-stone-500">lines</span> labelled as setup, punchline, tag, or fluff.</p>
            <p>Metrics include punch density and tag density per set.</p>
          </div>
        </div>

      </div>

      <div className="border-t border-stone-800">
        <div className="mx-auto max-w-6xl px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-stone-600">&copy; {new Date().getFullYear()} PunchNotes. All rights reserved.</p>
          <p className="text-xs text-stone-600">Data derived from publicly available Kill Tony recordings.</p>
        </div>
      </div>
    </footer>
  );
}
