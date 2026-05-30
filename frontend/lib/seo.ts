import type { Metadata } from 'next';
import type { FaqItem } from '@/types/FaqItem';

export const SITE_URL = 'https://www.punchpedia.com';
export const SITE_NAME = 'PunchPedia';

interface MetadataOptions {
  title: string;
  description?: string;
  canonicalPath?: string;
  noindex?: boolean;
}

export function buildMetadata({
  title,
  description,
  canonicalPath,
  noindex,
}: MetadataOptions): Metadata {
  const url = canonicalPath ? new URL(canonicalPath, SITE_URL).toString() : undefined;

  return {
    title,
    description,
    alternates: url ? { canonical: url } : undefined,
    openGraph: {
      title,
      description,
      url,
      siteName: SITE_NAME,
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
    robots: noindex ? { index: false, follow: false } : undefined,
  };
}

export function buildArticleSchema(options: {
  title: string;
  description: string;
  slug: string;
  authorName: string;
  datePublished: string;
  dateModified: string;
}): object {
  const url = `${SITE_URL}/articles/${options.slug}`;

  return {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: options.title,
    description: options.description,
    url,
    datePublished: `${options.datePublished}T00:00:00+00:00`,
    dateModified: `${options.dateModified}T00:00:00+00:00`,
    author: {
      '@type': 'Person',
      name: options.authorName,
      url: SITE_URL,
    },
    publisher: {
      '@type': 'Organization',
      name: SITE_NAME,
      url: SITE_URL,
    },
    isPartOf: {
      '@type': 'Blog',
      url: `${SITE_URL}/articles`,
      name: `${SITE_NAME} Articles`,
    },
    breadcrumb: {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Home', item: SITE_URL },
        { '@type': 'ListItem', position: 2, name: 'Articles', item: `${SITE_URL}/articles` },
        { '@type': 'ListItem', position: 3, name: options.title, item: url },
      ],
    },
  };
}

export function buildFaqSchema(faqData: FaqItem[]): object | null {
  if (!faqData.length) return null;

  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqData.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: faq.answer,
      },
    })),
  };
}
