export const metadata = {
  title: "About — PunchPedia",
  description: "What PunchPedia is and why it exists.",
};

export default function AboutPage() {
  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-2xl px-4 py-16 sm:px-6">
        <h1 className="text-3xl font-bold text-stone-900">About PunchPedia</h1>

        <div className="mt-8 space-y-6 text-stone-600 leading-relaxed">
          <p>
            PunchPedia (need a new name) is a system for analysing stand-up comedy at the structural level — connecting
            how jokes are built to how audiences actually respond.
          </p>

        </div>
      </div>
    </div>
  );
}
