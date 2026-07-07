import SetPlaylists from "./SetPlaylists";
import FilterControls from "@/components/FilterControls";
import { SET_SEARCH_CONFIG } from "@/lib/searchConfigs";
import ListPageHeader from "@/components/ListPageHeader";
import { SITE_URL, buildBreadcrumbSchema, buildMetadata } from "@/lib/seo";

export const metadata = buildMetadata({
  title: "Sets - Kill Tony | PunchNotes",
  description:
    "Browse all Kill Tony stand-up sets with joke breakdowns, transcripts, and comedian analytics.",
  canonicalPath: "/killtony/sets",
});

const schema = {
  '@context': 'https://schema.org',
  '@type': 'CollectionPage',
  name: 'Kill Tony Sets',
  description: 'Browse all Kill Tony stand-up sets with joke breakdowns, transcripts, and comedian analytics.',
  url: `${SITE_URL}/killtony/sets`,
  breadcrumb: buildBreadcrumbSchema([
    { name: 'Kill Tony', item: `${SITE_URL}/killtony` },
    { name: 'Sets', item: `${SITE_URL}/killtony/sets` },
  ]),
};

export default async function SetsBrowsePage() {
  return (
    <>
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
    />
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <ListPageHeader
          title="Sets"
          searchPlaceholder="Search sets..."
          searchPath="/killtony/sets/search"
          urlState={false}
          controls={<FilterControls config={SET_SEARCH_CONFIG} urlState={false} />}
        />
      </div>

      <div className="mx-auto max-w-6xl pb-12">
        <h2 className="mb-6 px-6 text-2xl font-bold tracking-tight text-stone-950">
          Set playlists
        </h2>
        <SetPlaylists />
      </div>
    </div>
    </>
  );
}
