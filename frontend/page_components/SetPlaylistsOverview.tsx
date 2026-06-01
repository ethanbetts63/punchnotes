import type { ComedianAttribute, SetListItem } from "@/lib/serverApi";
import { setToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type Playlist = {
  id: string;
  title: string;
  description: string;
  attribute: ComedianAttribute;
};

const PLAYLISTS: Playlist[] = [
  {
    id: "regular-first-sets",
    title: "Regular Debuts",
    description: "The first appearance of every comedian who became a regular.",
    attribute: "regular",
  },
  {
    id: "golden-ticket-first-sets",
    title: "Golden Ticket Debuts",
    description: "The first appearance of every comedian who went on to win a golden ticket.",
    attribute: "golden_ticket",
  },
];

function firstSetsFor(sets: SetListItem[], attribute: ComedianAttribute): SetListItem[] {
  const firstByComedian = new Map<number, SetListItem>();
  for (const set of sets) {
    if (!set.comedian.attributes.includes(attribute)) continue;
    const current = firstByComedian.get(set.comedian.id);
    if (
      !current ||
      set.episode.number < current.episode.number ||
      (set.episode.number === current.episode.number && set.start_seconds < current.start_seconds)
    ) {
      firstByComedian.set(set.comedian.id, set);
    }
  }
  return [...firstByComedian.values()].sort(
    (a, b) => a.episode.number - b.episode.number || a.start_seconds - b.start_seconds
  );
}

type Props = { sets: SetListItem[] };

export default function SetPlaylistsOverview({ sets }: Props) {
  const lists = PLAYLISTS.map((p) => ({
    ...p,
    items: firstSetsFor(sets, p.attribute),
  })).filter((p) => p.items.length > 0);

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
