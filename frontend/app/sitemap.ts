import type { MetadataRoute } from 'next';
import { SITE_URL } from '@/lib/seo';

export default function sitemap(): MetadataRoute.Sitemap {
  return [
    { url: `${SITE_URL}/killtony`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/episodes`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/comedians`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/sets`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/killtony/jokes`, lastModified: '2026-06-29' },
    { url: `${SITE_URL}/about`, lastModified: '2026-06-29' },
  ];
}
