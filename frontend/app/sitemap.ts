import type { MetadataRoute } from 'next';
import { COMEDIAN_LISTS } from '@/lib/playlists';
import { getServerComedians, getServerSets, getServerVideos } from '@/lib/serverApi';
import { SITE_URL } from '@/lib/seo';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [episodes, comedians, sets] = await Promise.all([getServerVideos(), getServerComedians(), getServerSets()]);
  // The playlists name comics before their sets are imported; only those with a page are listed.
  const existingComedianSlugs = new Set(comedians.map((comedian) => comedian.slug));
  const indexedComedianSlugs = Array.from(
    new Set(
      COMEDIAN_LISTS
        .filter((list) => list.id === 'regulars' || list.id === 'golden-ticket-winners')
        .flatMap((list) => list.slugs),
    ),
  ).filter((slug) => existingComedianSlugs.has(slug));

  const comedianUrls = indexedComedianSlugs.map((slug) => ({
    url: `${SITE_URL}/killtony/comedians/${slug}`,
    lastModified: '2026-07-02',
  }));

  // An episode with no sets is an empty template, and its page is noindex until it has some. Read from the sets
  // themselves, as the page does: the stored set_count lags.
  const episodeSlugsWithSets = new Set(sets.map((set) => set.video.slug));
  const episodeUrls = episodes
    .filter((episode) => episodeSlugsWithSets.has(episode.slug))
    .map((episode) => ({
      url: `${SITE_URL}/killtony/episodes/${episode.slug}`,
      lastModified: episode.date ?? '2026-07-02',
    }));

  const setUrls = sets
    .filter((set) => set.bit_count > 0)
    .map((set) => ({
      url: `${SITE_URL}/killtony/sets/${set.slug}`,
      lastModified: set.video.date ?? '2026-07-02',
    }));

  return [
    { url: `${SITE_URL}/killtony`, lastModified: '2026-07-12' },
    { url: `${SITE_URL}/killtony/episodes`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/comedians`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/sets`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/jokes`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/joke-originality-checker`, lastModified: '2026-07-10' },
    { url: `${SITE_URL}/about`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/articles`, lastModified: '2026-07-01' },
    { url: `${SITE_URL}/articles/how-to-annotate-jokes`, lastModified: '2026-07-01' },
    ...episodeUrls,
    ...comedianUrls,
    ...setUrls,
  ];
}
