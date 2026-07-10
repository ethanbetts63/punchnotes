import { Suspense } from "react";
import PlagiarismChecker from "./PlagiarismChecker";
import PlagiarismHowItWorks from "@/components/PlagiarismHowItWorks";
import { SITE_URL, buildMetadata } from "@/lib/seo";

const DESCRIPTION =
  "Free joke originality checker. Paste a joke to find the closest matching jokes in a database of annotated stand-up material, with line-by-line similarity highlights.";

export const metadata = buildMetadata({
  title: "Joke Originality Checker | PunchNotes",
  description: DESCRIPTION,
  canonicalPath: "/joke-originality-checker",
});

const schema = {
  '@context': 'https://schema.org',
  '@type': 'WebApplication',
  name: 'Joke Originality Checker',
  description: DESCRIPTION,
  url: `${SITE_URL}/joke-originality-checker`,
  applicationCategory: 'UtilityApplication',
  operatingSystem: 'Web',
  offers: {
    '@type': 'Offer',
    price: '0',
    priceCurrency: 'USD',
  },
};

export default function JokeOriginalityCheckerPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      <div className="min-h-screen bg-white">
        <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-stone-900">Joke Originality Checker</h1>
            <p className="mt-2 text-stone-500">
              Paste a joke to find the most similar jokes in the database.
            </p>
          </div>
          <Suspense>
            <PlagiarismChecker />
          </Suspense>

          <div className="mt-12">
            <PlagiarismHowItWorks />
          </div>
        </div>
      </div>
    </>
  );
}
