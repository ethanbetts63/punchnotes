import type { Metadata } from 'next';
import type { FaqItem } from '@/types/FaqItem';

export const SITE_URL = 'https://www.punchnotes.app';
export const SITE_NAME = 'PunchNotes';
export const SITE_LOGO_URL = `${SITE_URL}/punchnotes_logo_512x512.png`;
export const DEFAULT_OG_IMAGE_URL = `${SITE_URL}/killtony/kt-anime.png`;

const SITE_LOGO_IMAGE_OBJECT = {
  '@type': 'ImageObject',
  url: SITE_LOGO_URL,
  width: 512,
  height: 512,
};

interface MetadataOptions {
  title: string;
  description?: string;
  canonicalPath?: string;
  image?: string | null;
  noindex?: boolean;
}

export function buildMetadata({
  title,
  description,
  canonicalPath,
  image,
  noindex,
}: MetadataOptions): Metadata {
  const url = canonicalPath ? new URL(canonicalPath, SITE_URL).toString() : undefined;
  const imageUrl = image ?? DEFAULT_OG_IMAGE_URL;

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
      images: [{ url: imageUrl }],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [imageUrl],
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
      '@id': `${SITE_URL}/#organization`,
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

export function buildOrganizationSchema(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    '@id': `${SITE_URL}/#organization`,
    name: SITE_NAME,
    url: SITE_URL,
    image: SITE_LOGO_IMAGE_OBJECT,
    logo: SITE_LOGO_IMAGE_OBJECT,
  };
}

export function buildWebSiteSchema(): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: SITE_NAME,
    url: SITE_URL,
    description:
      'Structured analysis of stand-up comedy. Explore Kill Tony sets, comedians, and jokes broken down by premise, mechanism, and audience response.',
    publisher: {
      '@id': `${SITE_URL}/#organization`,
    },
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE_URL}/killtony/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  };
}

export function buildBreadcrumbSchema(
  items: { name: string; item: string }[]
): object {
  return {
    '@type': 'BreadcrumbList',
    itemListElement: items.map((crumb, index) => ({
      '@type': 'ListItem',
      position: index + 1,
      name: crumb.name,
      item: crumb.item,
    })),
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
