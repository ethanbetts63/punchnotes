interface ArticlePageMeta {
  title: string;
  description: string;
  publishedDate: string;
}

const metaBySlug: Record<string, ArticlePageMeta> = {};

export function getArticlePageMeta(slug: string): ArticlePageMeta | null {
  return metaBySlug[slug] ?? null;
}
