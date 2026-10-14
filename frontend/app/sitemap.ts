import type { MetadataRoute } from 'next';
import { getServerComedians } from '@/lib/serverApi';
import { SITE_URL, isIndexedComedian } from '@/lib/seo';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  // Search indexes comedian pages only. Sets and episodes are noindex, reached through the links on these pages.
  const comedians = await getServerComedians();
  const comedianUrls = comedians.filter(isIndexedComedian).map((comedian) => ({
    url: `${SITE_URL}/killtony/comedians/${comedian.slug}`,
  }));

  return [
    { url: `${SITE_URL}/killtony`, lastModified: '2026-07-12' },
    { url: `${SITE_URL}/killtony/episodes`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/comedians`, lastModified: '2026-10-14' },
    { url: `${SITE_URL}/killtony/sets`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/jokes`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/joke-originality-checker`, lastModified: '2026-07-10' },
    { url: `${SITE_URL}/about`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/articles`, lastModified: '2026-07-01' },
    { url: `${SITE_URL}/articles/how-to-annotate-jokes`, lastModified: '2026-07-01' },
    ...comedianUrls,
  ];
}
