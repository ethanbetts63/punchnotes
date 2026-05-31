import { getAllArticleMeta } from '@/lib/articles';
import { buildMetadata } from '@/lib/seo';
import ArticleListingPage from '@/page_components/ArticleListingPage';

export const metadata = buildMetadata({
  title: 'Articles | PunchNotes',
  description: 'Comedy analysis, breakdowns, and commentary on Kill Tony and stand-up comedy.',
  canonicalPath: '/articles',
});

export default function Page() {
  const articles = getAllArticleMeta();
  return <ArticleListingPage articles={articles} />;
}
