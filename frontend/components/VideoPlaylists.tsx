import type { Video } from "@/lib/serverApi";
import { VIDEO_PLAYLISTS } from "@/lib/playlists";
import { episodeToTile } from "@/lib/tiles";
import MediaCarousel from "@/components/MediaCarousel";

type Props = {
  episodes: Video[];
  limit?: number;
  itemLimit?: number;
};

export default function VideoPlaylists({ episodes, limit, itemLimit }: Props) {
  const byNumber = new Map(episodes.map((ep) => [String(ep.number), ep]));

  const lists = VIDEO_PLAYLISTS.map((list) => ({
    ...list,
    items: (list.slugs.map((slug) => byNumber.get(slug)).filter(Boolean) as Video[]).slice(0, itemLimit),
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
