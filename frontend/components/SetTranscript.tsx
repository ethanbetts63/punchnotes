"use client";

import { useState } from "react";
import type { Bit, Beat } from "@/lib/serverApi";

type Selected = { beat: Beat; bit: Bit; bitIdx: number; beatIdx: number };

const labelBadge: Record<string, string> = {
  setup:     "bg-blue-100 text-blue-700",
  punchline: "bg-amber-100 text-amber-700",
  tag:       "bg-green-100 text-green-700",
  fluff:     "bg-stone-100 text-stone-500",
};

function BeatPanel({
  beat, bitIdx, beatIdx,
}: {
  beat: Beat; bitIdx: number; beatIdx: number;
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white overflow-hidden shadow-sm">
      <div className="bg-stone-50 px-4 py-3 border-b border-stone-200">
        <p className="text-xs font-semibold uppercase tracking-wider text-stone-400">
          Bit {bitIdx + 1} · Beat {beatIdx + 1}
        </p>
        <p className="text-sm font-semibold text-stone-900 mt-0.5">Beat Details</p>
      </div>

      <div className="p-4 space-y-4">
        {beat.premise && (
          <div>
            <p className="text-xs uppercase tracking-wider font-semibold text-stone-400 mb-1">Beat Premise</p>
            <p className="text-sm italic text-stone-600">&ldquo;{beat.premise}&rdquo;</p>
          </div>
        )}

        {beat.joke_type && (
          <div>
            <p className="text-xs uppercase tracking-wider font-semibold text-stone-400 mb-1.5">Joke Type</p>
            <span className="inline-block text-xs font-semibold bg-stone-900 text-white px-2.5 py-1 rounded-full">
              {beat.joke_type}
            </span>
          </div>
        )}

        <div>
          <p className="text-xs uppercase tracking-wider font-semibold text-stone-400 mb-2">Lines</p>
          <div className="space-y-2">
            {beat.lines.filter((l) => l.label !== "fluff").map((line) => (
              <div key={line.id} className="flex gap-2 items-start">
                <span className={`shrink-0 text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${labelBadge[line.label]}`}>
                  {line.label}
                </span>
                <span className="text-sm text-stone-700 leading-snug">{line.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function firstAnnotatedBeat(bits: Bit[]): Selected | null {
  for (let bi = 0; bi < bits.length; bi++) {
    const bit = bits[bi];
    for (let bti = 0; bti < bit.beats.length; bti++) {
      const beat = bit.beats[bti];
      if (beat.lines.some((l) => l.label !== "fluff")) {
        return { beat, bit, bitIdx: bi, beatIdx: bti };
      }
    }
  }
  return null;
}

export default function SetTranscript({ bits }: { bits: Bit[] }) {
  const [selected, setSelected] = useState<Selected | null>(() => firstAnnotatedBeat(bits));

  function handleBeatClick(beat: Beat, bit: Bit, bitIdx: number, beatIdx: number) {
    setSelected({ beat, bit, bitIdx, beatIdx });
  }

  if (bits.length === 0) {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16 text-center text-stone-400">
        No beats annotated yet.
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <div className="flex gap-10 items-start">
        {/* Transcript */}
        <div className="flex-1 min-w-0">
          {bits.map((bit, bi) => (
            <div key={bit.id} className={bi > 0 ? "mt-10" : ""}>
              <p className="mb-4">
                <span className="bg-yellow-300 text-stone-900 font-semibold px-1 text-base">
                  [Bit {bi + 1}]
                </span>
              </p>

              {bit.beats.map((beat, bti) => {
                const hasAnnotated = beat.lines.some((l) => l.label !== "fluff");
                const isActive = selected?.beat.id === beat.id;

                return (
                  <div
                    key={beat.id}
                    role={hasAnnotated ? "button" : undefined}
                    tabIndex={hasAnnotated ? 0 : undefined}
                    className={[
                      bti > 0 ? "mt-3" : "",
                      "-mx-1 px-1 rounded",
                      hasAnnotated ? "cursor-pointer" : "",
                      isActive
                        ? "bg-yellow-300"
                        : hasAnnotated
                        ? "hover:bg-yellow-100"
                        : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={
                      hasAnnotated
                        ? () => handleBeatClick(beat, bit, bi, bti)
                        : undefined
                    }
                    onKeyDown={
                      hasAnnotated
                        ? (e) => {
                            if (e.key === "Enter" || e.key === " ") {
                              e.preventDefault();
                              handleBeatClick(beat, bit, bi, bti);
                            }
                          }
                        : undefined
                    }
                  >
                    {beat.lines.map((line) => (
                      <div
                        key={line.id}
                        className={[
                          "py-0.5 text-xl leading-relaxed",
                          "text-stone-900",
                        ].join(" ")}
                      >
                        {line.text}
                      </div>
                    ))}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Right panel — sticks to viewport as you scroll */}
        <div className="hidden md:block w-80 xl:w-96 shrink-0 sticky top-20 self-start">
          {selected && (
            <BeatPanel
              beat={selected.beat}
              bitIdx={selected.bitIdx}
              beatIdx={selected.beatIdx}
            />
          )}
        </div>
      </div>

      {/* Mobile panel — below transcript */}
      {selected && (
        <div className="md:hidden mt-8">
          <BeatPanel
            beat={selected.beat}
            bitIdx={selected.bitIdx}
            beatIdx={selected.beatIdx}
          />
        </div>
      )}
    </div>
  );
}
