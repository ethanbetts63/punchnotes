import type { MetadataRoute } from 'next';
import { SITE_URL } from '@/lib/seo';
import { getServerVideos, getServerComedians, getServerSets } from '@/lib/serverApi';
import { getAllArticleMeta } from '@/lib/articles';

const STATIC_ROUTES: MetadataRoute.Sitemap = [
  { url: `${SITE_URL}/killtony`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/killtony/episodes`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/killtony/comedians`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/killtony/sets`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/killtony/bits`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/killtony/jokes`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/articles`, lastModified: '2026-06-29' },
  { url: `${SITE_URL}/about`, lastModified: '2026-06-29' },
];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [episodes, comedians, sets] = await Promise.all([
    getServerVideos(),
    getServerComedians(),
    getServerSets(),
  ]);

  const episodeRoutes = (episodes ?? []).map((ep): MetadataRoute.Sitemap[number] => ({
    url: `${SITE_URL}/killtony/episodes/${ep.slug}`,
    lastModified: ep.date ?? '2026-06-29',
  }));

  const comedianRoutes = (comedians ?? []).map((c): MetadataRoute.Sitemap[number] => ({
    url: `${SITE_URL}/killtony/comedians/${c.slug}`,
    lastModified: '2026-06-29',
  }));

  const setRoutes = (sets ?? []).map((s): MetadataRoute.Sitemap[number] => ({
    url: `${SITE_URL}/killtony/sets/${s.slug}`,
    lastModified: s.video.date ?? '2026-06-29',
  }));

  const articleRoutes = getAllArticleMeta().map((a): MetadataRoute.Sitemap[number] => ({
    url: `${SITE_URL}/articles/${a.slug}`,
    lastModified: a.lastModified,
  }));

  return [...STATIC_ROUTES, ...episodeRoutes, ...comedianRoutes, ...setRoutes, ...articleRoutes];
}
