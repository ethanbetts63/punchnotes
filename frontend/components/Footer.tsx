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
              <Image src="/logo.png" alt="PunchNotes logo" width={44} height={44} className="object-cover w-full h-full"  />
            </div>
            <p className={LABEL_CLASS} style={{ marginBottom: 0 }}>PunchNotes</p>
          </div>
          <p className="text-sm text-stone-400 leading-relaxed">
            Structured comedy analytics for Kill Tony. Sets, comedians, and jokes broken
            down by joke mechanism, line structure, and audience response.
          </p>
          <p className="mt-4 text-sm text-stone-400">
            <a href="mailto:ethanbetts63@gmail.com" className="hover:text-stone-200 transition-colors duration-200">
              ethanbetts63@gmail.com
            </a>
          </p>
          <p className="mt-4 text-xs text-stone-600 leading-relaxed">
            Fan-made archive. Not affiliated with Kill Tony. If your content is on this site and you would like it removed, please contact me.
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
          <ul className="space-y-2 mb-8">
            <li><Link href="/about" className={LINK_CLASS}>About</Link></li>
          </ul>
          <p className={LABEL_CLASS}>Articles</p>
          <ul className="space-y-2">
            <li><Link href="/articles/how-to-annotate-jokes" className={LINK_CLASS}>How to Annotate Jokes</Link></li>
          </ul>
        </div>

      </div>

      <div className="border-t border-stone-800">
        <div className="mx-auto max-w-6xl px-6 py-5 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-stone-600">&copy; {new Date().getFullYear()} PunchNotes. All rights reserved.</p>
          <a
            href="https://www.freethedesk.com.au/"
            target="_blank"
            rel="nofollow noopener noreferrer"
            className="flex items-center gap-1.5 text-xs text-stone-600 transition-opacity hover:opacity-70"
            aria-label="Developed by freethedesk"
          >
            <span>Developed by</span>
            <Image src="/freethedesk_logo_512x512.png" alt="" width={22} height={22} className="h-[22px] w-[22px]" />
            <span className="font-black leading-none tracking-[-0.085em] text-stone-200">
              free<span className="text-[#1a5fa8]">the</span>desk
              <span className="text-[#0b64d6]">.</span>
            </span>
          </a>
        </div>
      </div>
    </footer>
  );
}
