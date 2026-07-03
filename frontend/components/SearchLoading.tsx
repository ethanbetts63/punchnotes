import { Loader2 } from "lucide-react";

export default function SearchLoading({ title }: { title: string }) {
  return (
    <div className="min-h-screen bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-stone-900">{title}</h1>
        </div>
        <div className="flex items-center justify-center py-24">
          <Loader2 className="h-8 w-8 animate-spin text-stone-400" />
        </div>
      </div>
    </div>
  );
}
