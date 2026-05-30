import Link from "next/link";
import type { BitListItem } from "@/lib/serverApi";
import { BIT_LISTS } from "@/lib/playlists";

type Props = { bits: BitListItem[] };

export default function BitPlaylists({ bits }: Props) {
  const byId = new Map(bits.map((b) => [b.id, b]));

  const lists = BIT_LISTS.map((list) => ({
    ...list,
    items: list.ids.map((id) => byId.get(id)).filter(Boolean) as BitListItem[],
  })).filter((list) => list.items.length > 0);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-8">
      {lists.map((list) => (
        <section key={list.id}>
          <div className="mb-3">
            <h2 className="text-sm font-bold text-stone-950">{list.title}</h2>
            <p className="mt-0.5 text-xs text-stone-500">{list.description}</p>
          </div>
          <div className="flex gap-3 overflow-x-auto pb-2">
            {list.items.map((bit) => (
              <Link
                key={bit.id}
                href={`/killtony/sets/${bit.set_id}`}
                className="group w-64 shrink-0 overflow-hidden rounded-lg border border-stone-200 bg-white p-3 transition-colors hover:border-primary/40 hover:shadow-sm"
              >
                <p className="text-[11px] font-bold uppercase tracking-wide text-primary">
                  {bit.comedian}
                </p>
                <p className="mt-0.5 text-xs text-stone-500">Ep {bit.episode_number}</p>
                {bit.summary && (
                  <p className="mt-2 line-clamp-3 text-sm italic text-stone-600 transition-colors group-hover:text-stone-900">
                    &ldquo;{bit.summary}&rdquo;
                  </p>
                )}
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
