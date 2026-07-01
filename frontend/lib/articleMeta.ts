interface ArticlePageMeta {
  title: string;
  description: string;
  publishedDate: string;
}

const metaBySlug: Record<string, ArticlePageMeta> = {
  'how-we-classify-jokes': {
    title: 'How We Classify Jokes',
    description:
      "Every joke in the Kill Tony database is annotated at the line level and assigned one of nine structural types. Here's exactly how that works.",
    publishedDate: '2026-07-01',
  },
};

export function getArticlePageMeta(slug: string): ArticlePageMeta | null {
  return metaBySlug[slug] ?? null;
}
