import { Suspense } from "react";
import { ChevronDown } from "lucide-react";
import PlagiarismChecker from "./PlagiarismChecker";
import PlagiarismHowItWorks from "@/components/PlagiarismHowItWorks";
import { SITE_URL, buildFaqSchema, buildMetadata } from "@/lib/seo";
import type { FaqItem } from "@/types/FaqItem";

const DESCRIPTION =
  "Free joke originality checker. Paste a joke to find the closest matching jokes in a database of annotated stand-up material, with line-by-line similarity highlights.";

export const metadata = buildMetadata({
  title: "Joke Originality Checker | PunchNotes",
  description: DESCRIPTION,
  canonicalPath: "/joke-originality-checker",
});

const faqData: FaqItem[] = [
  {
    question: "How do I check if my joke has already been done?",
    answer:
      "Paste your joke into the checker above. It searches a database of annotated stand-up jokes using semantic similarity — matching ideas and phrasing, not just exact words — and shows the closest matches with line-by-line highlights.",
  },
  {
    question: "What does the similarity percentage mean?",
    answer:
      "It measures how close the meaning of your text is to a joke in the database. A high score means the ideas and structure closely overlap. It is a measure of similarity, not proof that either joke was copied.",
  },
  {
    question: "Does a high match mean a joke was stolen?",
    answer:
      "Not necessarily. Comedians independently arrive at similar ideas all the time — this is known as parallel thinking. A high match is a signal worth reviewing, not an accusation of joke theft. Click through to the original set and judge the context yourself.",
  },
  {
    question: "What jokes does it check against?",
    answer:
      "A growing database of stand-up material annotated joke by joke, with each line labelled as setup, punchline, or tag. Coverage is expanding all the time.",
  },
];

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

const faqSchema = buildFaqSchema(faqData);

function FaqBlock() {
  return (
    <section>
      <h2 className="mb-6 text-2xl font-bold text-stone-900">FAQ</h2>
      <div className="space-y-3">
        {faqData.map((faq) => (
          <details
            key={faq.question}
            className="group rounded-xl border border-stone-200 bg-white"
          >
            <summary className="flex cursor-pointer list-none items-center justify-between gap-4 px-5 py-4 marker:hidden">
              <h3 className="text-sm font-semibold text-stone-900">{faq.question}</h3>
              <ChevronDown className="h-4 w-4 shrink-0 text-stone-400 transition-transform duration-300 group-open:rotate-180" />
            </summary>
            <p className="px-5 pb-5 text-sm leading-relaxed text-stone-500">{faq.answer}</p>
          </details>
        ))}
      </div>
    </section>
  );
}

export default function JokeOriginalityCheckerPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      {faqSchema && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }}
        />
      )}
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

          <div className="mt-12">
            <FaqBlock />
          </div>
        </div>
      </div>
    </>
  );
}
