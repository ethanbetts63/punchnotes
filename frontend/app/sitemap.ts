import type { MetadataRoute } from 'next';
import { COMEDIAN_LISTS } from '@/lib/playlists';
import { getServerVideos } from '@/lib/serverApi';
import { SITE_URL } from '@/lib/seo';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const episodes = await getServerVideos();
  const indexedComedianSlugs = Array.from(
    new Set(
      COMEDIAN_LISTS
        .filter((list) => list.id === 'regulars' || list.id === 'golden-ticket-winners')
        .flatMap((list) => list.slugs),
    ),
  );

  const comedianUrls = indexedComedianSlugs.map((slug) => ({
    url: `${SITE_URL}/killtony/comedians/${slug}`,
    lastModified: '2026-07-02',
  }));

  const episodeUrls = episodes.map((episode) => ({
    url: `${SITE_URL}/killtony/episodes/${episode.slug}`,
    lastModified: episode.date ?? '2026-07-02',
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
  ];
}
