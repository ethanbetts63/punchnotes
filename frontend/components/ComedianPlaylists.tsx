import Link from "next/link";
import type { Comedian } from "@/lib/serverApi";
import { COMEDIAN_LISTS } from "@/lib/playlists";
import ComedianImage from "@/components/ComedianImage";

type Props = { comedians: Comedian[] };

export default function ComedianPlaylists({ comedians }: Props) {
  const byId = new Map(comedians.map((c) => [c.id, c]));

  const lists = COMEDIAN_LISTS.map((list) => ({
    ...list,
    items: list.ids.map((id) => byId.get(id)).filter(Boolean) as Comedian[],
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
            {list.items.map((c) => (
              <Link
                key={c.id}
                href={`/killtony/comedians/${c.slug}`}
                className="group w-40 shrink-0 overflow-hidden rounded-lg border border-stone-200 bg-white transition-colors hover:border-primary/40 hover:shadow-sm"
              >
                <ComedianImage
                  imageUrl={c.image_url}
                  name={c.name}
                  className="h-40 w-full"
                />
                <div className="p-2.5">
                  <p className="truncate text-sm font-bold leading-tight text-stone-950 transition-colors group-hover:text-primary">
                    {c.name}
                  </p>
                  <p className="mt-1 text-xs text-stone-500">
                    {c.set_count} set{c.set_count !== 1 ? "s" : ""}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
