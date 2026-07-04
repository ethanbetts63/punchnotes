import type { Comedian } from "@/lib/serverApi";
import { COMEDIAN_LISTS } from "@/lib/playlists";
import { comedianToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type Props = {
  comedians: Comedian[];
  limit?: number;
};

export default function ComedianPlaylists({ comedians, limit }: Props) {
  const bySlug = new Map(comedians.map((c) => [c.slug, c]));

  const lists = COMEDIAN_LISTS.map((list) => ({
    ...list,
    items: list.slugs.map((slug) => bySlug.get(slug)).filter(Boolean) as Comedian[],
  }))
    .filter((list) => list.items.length > 0)
    .slice(0, limit);

  if (lists.length === 0) return null;

  return (
    <div className="space-y-10">
      {lists.map((list) => (
        <MediaCarousel
          key={list.id}
          title={list.title}
          description={list.description}
          items={list.items.map(comedianToTile)}
        />
      ))}
    </div>
  );
}
