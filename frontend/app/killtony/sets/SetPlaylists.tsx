import type { SetListItem } from "@/lib/serverApi";
import { SET_LISTS } from "@/lib/playlists";
import { setToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type Props = { sets: SetListItem[] };

export default function SetPlaylists({ sets }: Props) {
  const byId = new Map(sets.map((s) => [s.id, s]));

  const lists = SET_LISTS.map((list) => ({
    ...list,
    items: list.ids.map((id) => byId.get(id)).filter(Boolean) as SetListItem[],
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
