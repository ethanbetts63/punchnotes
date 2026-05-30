import type { FaqItem } from '@/types/FaqItem';

const faqsBySlug: Record<string, FaqItem[]> = {};

export function getArticleFaqs(slug: string): FaqItem[] {
  return faqsBySlug[slug] ?? [];
}
