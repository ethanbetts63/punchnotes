"use client";

import { useEffect, useRef } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import type { Bit, Beat } from "@/lib/serverApi";
import { lineLabelBadge } from "@/lib/killTonyDisplay";

type Selected = { beat: Beat; bit: Bit; bitIdx: number; beatIdx: number };

function BeatPanel({
  beat,
  bitIdx,
  beatIdx,
}: {
  beat: Beat;
  bitIdx: number;
  beatIdx: number;
}) {
  return (
    <div className="overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm">
      <div className="border-b border-stone-200 bg-stone-50 px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-wider text-stone-400">
          Bit {bitIdx + 1} · Beat {beatIdx + 1}
        </p>
        <p className="mt-0.5 text-sm font-semibold text-stone-900">Beat Details</p>
      </div>

      <div className="space-y-4 p-4">
        {beat.premise && (
          <div>
            <p className="mb-1 text-xs font-semibold uppercase tracking-wider text-stone-400">Beat Premise</p>
            <p className="text-sm italic text-stone-600">&ldquo;{beat.premise}&rdquo;</p>
          </div>
        )}

        {beat.joke_type && (
          <div>
            <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-stone-400">Joke Type</p>
            <span className="inline-block rounded-full bg-stone-900 px-2.5 py-1 text-xs font-semibold text-white">
              {beat.joke_type}
            </span>
          </div>
        )}

        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-stone-400">Lines</p>
          <div className="space-y-2">
            {beat.lines.filter((line) => line.label !== "fluff").map((line) => (
              <div key={line.id} className="flex items-start gap-2">
                <span className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-bold uppercase ${lineLabelBadge[line.label]}`}>
                  {line.label}
                </span>
                <span className="text-sm leading-snug text-stone-700">{line.text}</span>
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
      if (beat.lines.some((line) => line.label !== "fluff")) {
        return { beat, bit, bitIdx: bi, beatIdx: bti };
      }
    }
  }
  return null;
}

function selectedFromIndices(bits: Bit[], bitIdx: number, beatIdx: number): Selected | null {
  const bit = bits[bitIdx];
  const beat = bit?.beats[beatIdx];
  if (!bit || !beat || !beat.lines.some((line) => line.label !== "fluff")) return null;
  return { beat, bit, bitIdx, beatIdx };
}

export default function SetTranscript({
  bits,
}: {
  bits: Bit[];
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const activeBeatRef = useRef<HTMLDivElement | null>(null);
  const selected = (() => {
    const rawBitId = searchParams.get("bit");
    const rawBeatIndex = searchParams.get("beat");

    if (rawBitId) {
      const bitId = Number(rawBitId);
      const beatIndex = Number(rawBeatIndex ?? "0");
      if (Number.isFinite(bitId) && Number.isInteger(beatIndex) && beatIndex >= 0) {
        const bitIdx = bits.findIndex((bit) => bit.id === bitId);
        if (bitIdx >= 0) {
          const fromUrl = selectedFromIndices(bits, bitIdx, beatIndex);
          if (fromUrl) return fromUrl;
        }
      }
    }

    return firstAnnotatedBeat(bits);
  })();

  useEffect(() => {
    const activeElement = activeBeatRef.current;
    if (!activeElement) return;

    const frame = window.requestAnimationFrame(() => {
      const y = activeElement.getBoundingClientRect().top + window.scrollY - 96;
      window.scrollTo({ top: Math.max(0, y), behavior: "smooth" });
    });

    return () => window.cancelAnimationFrame(frame);
  }, [selected?.beat.id]);

  function updateUrl(bit: Bit, beatIdx: number) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("bit", String(bit.id));
    params.set("beat", String(beatIdx));
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }

  function handleBeatClick(beat: Beat, bit: Bit, bitIdx: number, beatIdx: number) {
    updateUrl(bit, beatIdx);
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
      <div className="flex items-start gap-10">
        <div className="min-w-0 flex-1">
          {bits.map((bit, bi) => (
            <div key={bit.id} className={bi > 0 ? "mt-10" : ""}>
              <p className="mb-4">
                <span className="bg-yellow-300 px-1 text-base font-semibold text-stone-900">
                  [Bit {bi + 1}]
                </span>
              </p>

              {bit.beats.map((beat, bti) => {
                const hasAnnotated = beat.lines.some((line) => line.label !== "fluff");
                const isActive = selected?.beat.id === beat.id;

                return (
                  <div
                    key={beat.id}
                    ref={isActive ? activeBeatRef : null}
                    role={hasAnnotated ? "button" : undefined}
                    tabIndex={hasAnnotated ? 0 : undefined}
                    className={[
                      bti > 0 ? "mt-3" : "",
                      "-mx-1 rounded px-1",
                      hasAnnotated ? "cursor-pointer" : "",
                      isActive
                        ? "bg-yellow-300"
                        : hasAnnotated
                          ? "hover:bg-yellow-100"
                          : "",
                    ].filter(Boolean).join(" ")}
                    onClick={hasAnnotated ? () => handleBeatClick(beat, bit, bi, bti) : undefined}
                    onKeyDown={hasAnnotated ? (event) => {
                      if (event.key === "Enter" || event.key === " ") {
                        event.preventDefault();
                        handleBeatClick(beat, bit, bi, bti);
                      }
                    } : undefined}
                  >
                    {beat.lines.map((line) => (
                      <div
                        key={line.id}
                        className="py-0.5 text-xl leading-relaxed text-stone-900"
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

        <div className="sticky top-20 hidden w-80 shrink-0 self-start md:block xl:w-96">
          {selected && (
            <BeatPanel
              beat={selected.beat}
              bitIdx={selected.bitIdx}
              beatIdx={selected.beatIdx}
            />
          )}
        </div>
      </div>

      {selected && (
        <div className="mt-8 md:hidden">
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
