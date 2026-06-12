import type { Episode } from "@/lib/serverApi";
import { EPISODE_LISTS } from "@/lib/playlists";
import { episodeToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type Props = {
  episodes: Episode[];
  limit?: number;
};

export default function EpisodePlaylists({ episodes, limit }: Props) {
  const byId = new Map(episodes.map((ep) => [ep.id, ep]));
  const byNumber = new Map(episodes.map((ep) => [ep.number, ep]));

  const lists = EPISODE_LISTS.map((list) => ({
    ...list,
    items: list.ids
      .map((id) => (list.matchBy === "number" ? byNumber : byId).get(id))
      .filter(Boolean) as Episode[],
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
          items={list.items.map(episodeToTile)}
        />
      ))}
    </div>
  );
}
