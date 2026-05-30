import { Card, CardContent } from "./ui/card";
import { ChevronDown } from 'lucide-react';
import type { FaqItem } from '@/types/FaqItem';

interface Props {
  title: string;
  faqData: FaqItem[];
}

export const FaqSection = ({ title, faqData }: Props) => {
  return (
    <div className="py-8 bg-stone-900">
      <div className="container mx-auto px-4">
        <h2 className="text-4xl font-bold text-center text-white mb-8">{title}</h2>
        <div className="flex flex-col items-center gap-4">
          {faqData.map((faq, index) => (
            <div key={index} className="w-full md:w-2/3 lg:w-2/3">
              <Card className="bg-white text-stone-900 rounded-lg shadow-md">
                <CardContent className="p-0">
                  <details className="group">
                    <summary className="flex cursor-pointer list-none items-center justify-between gap-4 p-4 marker:hidden">
                      <h3 className="text-xl font-semibold text-stone-900">{faq.question}</h3>
                      <ChevronDown className="h-6 w-6 shrink-0 text-stone-500 transition-transform duration-300 group-open:rotate-180" />
                    </summary>
                    <div className="px-6 pb-6 pt-2">
                      <p className="text-stone-600 text-lg">{faq.answer}</p>
                    </div>
                  </details>
                </CardContent>
              </Card>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
