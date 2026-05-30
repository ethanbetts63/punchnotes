import Link from 'next/link';
import type { ArticleMeta } from '@/lib/articles';

interface Props {
  articles: ArticleMeta[];
}

export default function ArticleListingPage({ articles }: Props) {
  const dateFormatter = new Intl.DateTimeFormat('en-AU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900">Articles</h1>
          <p className="mt-2 text-stone-500">Comedy analysis, breakdowns, and commentary.</p>
        </div>

        {articles.length === 0 ? (
          <div className="rounded-xl border border-stone-200 bg-stone-50 p-12 text-center">
            <p className="text-stone-500">No articles published yet.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {articles.map((article) => {
              const publishedDate = dateFormatter.format(
                new Date(`${article.publishedDate}T00:00:00+00:00`),
              );

              return (
                <Link
                  key={article.slug}
                  href={`/articles/${article.slug}`}
                  className="group flex flex-col border border-stone-200 rounded-xl p-6 hover:border-primary/50 hover:shadow-sm transition-all duration-200 bg-white"
                >
                  <p className="text-primary text-[10px] font-bold uppercase tracking-[0.25em] mb-3">
                    By {article.authorName} | <time dateTime={article.publishedDate}>{publishedDate}</time>
                  </p>
                  <h2 className="text-lg font-semibold text-stone-900 group-hover:text-primary transition-colors duration-200 mb-3 leading-snug">
                    {article.title}
                  </h2>
                  <p className="text-sm text-stone-500 leading-relaxed mb-5 flex-1">
                    {article.excerpt}
                  </p>
                  <span className="text-sm font-medium text-primary">
                    Read article →
                  </span>
                </Link>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
