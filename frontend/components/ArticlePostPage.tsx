import Link from 'next/link';
import { FaqSection } from '@/components/FaqSection';
import type { Article } from '@/lib/articles';
import type { FaqItem } from '@/types/FaqItem';

interface Props {
  article: Article;
  faqs: FaqItem[];
}

export default function ArticlePostPage({ article, faqs }: Props) {
  const publishedDate = new Intl.DateTimeFormat('en-AU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  }).format(new Date(`${article.publishedDate}T00:00:00+00:00`));

  return (
    <>
      <div className="bg-white">
        <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">

          <nav className="flex items-center gap-2 text-xs text-stone-500 mb-8">
            <Link href="/" className="hover:text-primary transition-colors">Home</Link>
            <span>/</span>
            <Link href="/articles" className="hover:text-primary transition-colors">Articles</Link>
            <span>/</span>
            <span className="text-stone-900">{article.title}</span>
          </nav>

          <h1 className="text-3xl font-bold text-stone-900 mb-4 leading-snug">{article.title}</h1>

          <p className="text-xs font-bold uppercase tracking-[0.22em] text-primary mb-8">
            By {article.authorName} | Published <time dateTime={article.publishedDate}>{publishedDate}</time>
          </p>

          <article
            className="prose-article"
            dangerouslySetInnerHTML={{ __html: article.html }}
          />

          <div className="mt-12 pt-8 border-t border-stone-200">
            <Link href="/articles" className="text-sm text-primary hover:underline">
              ← Back to all articles
            </Link>
          </div>

        </div>
      </div>

      {faqs.length > 0 && (
        <FaqSection title="Frequently Asked Questions" faqData={faqs} />
      )}
    </>
  );
}
