import { getServerSets } from "@/lib/serverApi";
import type { SetListItem } from "@/lib/serverApi";
import { SET_LISTS } from "@/lib/playlists";
import { setToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

export default async function SetPlaylists() {
  const allSlugs = SET_LISTS.flatMap((l) => l.slugs);
  if (allSlugs.length === 0) return null;

  const sets = await getServerSets(`slugs=${allSlugs.join(",")}`);
  const bySlug = new Map((sets ?? []).map((s) => [s.slug, s]));

  const lists = SET_LISTS.map((list) => ({
    ...list,
    items: list.slugs.map((slug) => bySlug.get(slug)).filter(Boolean) as SetListItem[],
  })).filter((list) => list.items.length > 0);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-10">
      {lists.map((list) => (
        <MediaCarousel
          key={list.id}
          title={list.title}
          description={list.description}
          items={list.items.map(setToTile)}
        />
      ))}
    </div>
  );
}
