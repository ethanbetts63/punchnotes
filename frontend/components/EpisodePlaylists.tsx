import type { Video } from "@/lib/serverApi";
import { EPISODE_LISTS } from "@/lib/playlists";
import { episodeToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type Props = {
  episodes: Video[];
  limit?: number;
};

export default function VideoPlaylists({ episodes, limit }: Props) {
  const byNumber = new Map(episodes.map((ep) => [String(ep.number), ep]));

  const lists = EPISODE_LISTS.map((list) => ({
    ...list,
    items: list.slugs.map((slug) => byNumber.get(slug)).filter(Boolean) as Video[],
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
