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

  const today = '2026-07-11';

  const comedianUrls = indexedComedianSlugs.map((slug) => ({
    url: `${SITE_URL}/killtony/comedians/${slug}`,
    lastModified: today,
  }));

  const episodeUrls = episodes.map((episode) => ({
    url: `${SITE_URL}/killtony/episodes/${episode.slug}`,
    lastModified: episode.date ?? today,
  }));

  return [
    { url: `${SITE_URL}/killtony`, lastModified: today },
    { url: `${SITE_URL}/killtony/episodes`, lastModified: today },
    { url: `${SITE_URL}/killtony/comedians`, lastModified: today },
    { url: `${SITE_URL}/killtony/sets`, lastModified: today },
    { url: `${SITE_URL}/killtony/jokes`, lastModified: today },
    { url: `${SITE_URL}/joke-originality-checker`, lastModified: today },
    { url: `${SITE_URL}/about`, lastModified: today },
    { url: `${SITE_URL}/articles`, lastModified: today },
    { url: `${SITE_URL}/articles/how-to-annotate-jokes`, lastModified: today },
    ...episodeUrls,
    ...comedianUrls,
  ];
}
