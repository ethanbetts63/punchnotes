import type { MetadataRoute } from 'next';
import { SITE_URL } from '@/lib/seo';

const DISALLOWED_ROUTES = [
  '/api/',
  '/killtony/episodes/search',
  '/killtony/comedians/search',
  '/killtony/sets/search',
  '/killtony/bits/search',
  '/killtony/jokes/search',
  '/killtony/search',
];

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: DISALLOWED_ROUTES,
      },
      {
        userAgent: ['GPTBot', 'OAI-SearchBot', 'ClaudeBot', 'PerplexityBot', 'anthropic-ai', 'CCBot'],
        allow: '/',
        disallow: ['/api/'],
      },
    ],
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
