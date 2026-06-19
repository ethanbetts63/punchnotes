import type { Video } from "@/lib/serverApi";
import { fmtDate, fmtDuration, fmtCompact, getEpisodeGuestLabel } from "@/lib/killTonyDisplay";
import YoutubeThumbnail from "@/components/YoutubeThumbnail";
import SearchResultTile from "@/components/SearchResultTile";

export default function VideoSearchResults({ episodes }: { episodes: Video[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {episodes.map((episode) => {
        const likeRatio =
          episode.view_like_ratio != null
            ? episode.view_like_ratio.toFixed(1)
            : null;
        const guestLabel = getEpisodeGuestLabel(episode, `Kill Tony #${episode.number}`);

        return (
          <SearchResultTile
            key={episode.id}
            href={`/killtony/episodes/${episode.id}`}
            eyebrow={`Episode ${episode.number}`}
            title={guestLabel}
            subtitle={fmtDate(episode.date) || undefined}
            image={
              <YoutubeThumbnail
                videoId={episode.youtube_id}
                alt={`Episode ${episode.number} - ${guestLabel}`}
                className="absolute inset-0 h-full w-full"
              />
            }
            stats={[
              { label: "Duration", value: fmtDuration(episode.duration_seconds) },
              { label: "Sets", value: episode.set_count },
              { label: "Bucket pulls", value: episode.bucket_pull_count },
              { label: "Golden tickets", value: episode.golden_ticket_count },
              { label: "Big joke books", value: episode.large_joke_book_count },
              { label: "Regulars", value: episode.regular_count },
              ...(episode.view_count != null
                ? [{ label: "Views", value: fmtCompact(episode.view_count) }]
                : []),
              ...(episode.like_count != null
                ? [{ label: "Likes", value: fmtCompact(episode.like_count) }]
                : []),
              ...(episode.comment_count != null
                ? [{ label: "Comments", value: fmtCompact(episode.comment_count) }]
                : []),
              ...(likeRatio ? [{ label: "Views/like", value: likeRatio }] : []),
            ]}
          />
        );
      })}
    </div>
  );
}
