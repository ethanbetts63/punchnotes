import { notFound } from 'next/navigation';
import { getAllArticleSlugs, getArticleBySlug } from '@/lib/articles';
import { getArticleFaqs } from '@/lib/articleFaqs';
import { getArticlePageMeta } from '@/lib/articleMeta';
import { buildMetadata, buildArticleSchema, buildFaqSchema, SITE_URL } from '@/lib/seo';
import ArticlePostPage from '@/page_components/ArticlePostPage';
import type { Metadata } from 'next';

export const dynamicParams = false;

export function generateStaticParams() {
  return getAllArticleSlugs().map((slug) => ({ slug }));
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const article = await getArticleBySlug(slug);
  if (!article) return buildMetadata({ title: 'Not Found', noindex: true });

  const pageMeta = getArticlePageMeta(slug);
  const title = pageMeta?.title ?? article.title;
  const description = pageMeta?.description ?? article.excerpt;

  return {
    ...buildMetadata({
      title,
      description,
      canonicalPath: `/articles/${slug}`,
    }),
    openGraph: {
      title,
      description,
      url: `${SITE_URL}/articles/${slug}`,
      type: 'article',
    },
  };
}

export default async function Page({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const article = await getArticleBySlug(slug);
  if (!article) notFound();

  const faqs = getArticleFaqs(slug);

  const structuredData = [
    buildArticleSchema({
      title: article.title,
      description: article.excerpt,
      slug,
      authorName: article.authorName,
      datePublished: article.publishedDate,
      dateModified: article.lastModified,
    }),
    buildFaqSchema(faqs),
  ].filter(Boolean) as object[];

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      <ArticlePostPage article={article} faqs={faqs} />
    </>
  );
}
