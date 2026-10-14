import type { Comedian, ComedianDetail, Set, SetInComedian } from "@/lib/serverApi";
import { fmt2, fmtDate } from "@/lib/killTonyDisplay";
import { JOKE_TYPES } from "@/lib/jokeTypes";

function plural(count: number, singular: string, pluralForm = `${singular}s`) {
  return `${count} ${count === 1 ? singular : pluralForm}`;
}

function metric(value: number | null, label: string) {
  return value == null ? null : `${fmt2(value)} ${label}`;
}

function episodeLabel(set: SetInComedian): string {
  const date = fmtDate(set.video.date);
  return `episode #${set.video.number}${date ? ` (${date})` : ""}`;
}

function listJoin(items: string[]): string {
  if (items.length <= 1) return items.join("");
  return `${items.slice(0, -1).join(", ")} and ${items.at(-1)}`;
}

function jokeTypeLabel(id: string): string {
  return JOKE_TYPES.find((type) => type.id === id)?.label ?? id;
}

/** Oldest first, so "first" and "latest" read off the ends. */
function setsInOrder(comedian: ComedianDetail): SetInComedian[] {
  return [...comedian.sets].sort((a, b) => a.video.number - b.video.number);
}

export function getComedianTitle(comedian: ComedianDetail): string {
  const count = comedian.sets.length;
  return `${comedian.name} on Kill Tony: ${count === 1 ? "Set" : `${count} Sets`} and Jokes | PunchNotes`;
}

function appearanceFact(comedian: ComedianDetail): string {
  const sets = setsInOrder(comedian);
  if (sets.length === 0) return `${comedian.name} has appeared on Kill Tony, but PunchNotes has not indexed a set yet.`;
  if (sets.length === 1) return `${comedian.name} has done one set on Kill Tony, on ${episodeLabel(sets[0])}.`;
  return `${comedian.name} has done ${sets.length} sets on Kill Tony, the first on ${episodeLabel(sets[0])} and the latest on ${episodeLabel(sets[sets.length - 1])}.`;
}

function statusFact(comedian: ComedianDetail): string | null {
  if (comedian.attributes.includes("regular")) return `${comedian.name} is one of the show's regulars.`;
  if (comedian.attributes.includes("golden_ticket")) {
    return `${comedian.name} won a Golden Ticket, Tony's promise of a spot on a future episode.`;
  }
  if (comedian.attributes.includes("bucket_pull")) {
    return `${comedian.name} came to the show as a bucket pull, a comic whose name is drawn from the bucket for a one-minute set.`;
  }
  return null;
}

function panelFact(comedian: ComedianDetail): string | null {
  const guests: string[] = [];
  for (const set of [...setsInOrder(comedian)].reverse()) {
    for (const guest of set.video.guests ?? []) {
      const name = guest.trim();
      if (name && !guests.includes(name)) guests.push(name);
    }
  }
  if (guests.length === 0) return null;
  const shown = guests.slice(0, 4);
  return comedian.sets.length === 1
    ? `The guest panel that night was ${listJoin(shown)}.`
    : `${comedian.name} has performed for guest panels including ${listJoin(shown)}.`;
}

function punchDensityFact(comedian: ComedianDetail, peers: Comedian[]): string | null {
  const value = comedian.avg_punch_density;
  if (value == null) return null;
  const others = peers.filter((peer) => peer.avg_punch_density != null && peer.slug !== comedian.slug);
  const sentence = `${comedian.name} averages ${fmt2(value)} laugh lines, punchlines and tags, for every setup or filler line.`;
  if (others.length < 20) return sentence;
  const below = others.filter((peer) => (peer.avg_punch_density as number) < value).length;
  const percent = Math.round((below / others.length) * 100);
  return percent >= 50
    ? `${sentence} That is more than ${percent}% of the ${others.length.toLocaleString("en-US")} other comics PunchNotes has broken down.`
    : `${sentence} That is fewer than ${100 - percent}% of the ${others.length.toLocaleString("en-US")} other comics PunchNotes has broken down.`;
}

function trendFact(comedian: ComedianDetail): string | null {
  const measured = setsInOrder(comedian).filter((set) => set.punch_density != null);
  if (measured.length < 3) return null;
  const first = measured[0].punch_density as number;
  const latest = measured[measured.length - 1].punch_density as number;
  if (fmt2(first) === fmt2(latest)) return null;
  return `${comedian.name}'s punch density went from ${fmt2(first)} in the first set to ${fmt2(latest)} in the latest.`;
}

function tagFact(comedian: ComedianDetail): string | null {
  const value = comedian.avg_tag_density;
  if (value == null || value === 0) return null;
  return `On average ${comedian.name} follows each punchline with ${fmt2(value)} tags.`;
}

function jokeTypeFact(comedian: ComedianDetail): string | null {
  const counts = Object.entries(comedian.joke_type_counts ?? {}).sort((a, b) => b[1] - a[1]);
  const total = counts.reduce((sum, [, count]) => sum + count, 0);
  if (total < 3) return null;
  const [top, topCount] = counts[0];
  const next = counts[1];
  const lead = `Of the ${total} jokes PunchNotes has classified, ${topCount} are ${jokeTypeLabel(top)} jokes`;
  return next ? `${lead}, ahead of ${jokeTypeLabel(next[0])} (${next[1]}).` : `${lead}.`;
}

/** Plain statements drawn from the comedian's own sets, so no two comedian pages read alike. */
export function getComedianFacts(comedian: ComedianDetail, peers: Comedian[]): string[] {
  return [
    appearanceFact(comedian),
    statusFact(comedian),
    panelFact(comedian),
    punchDensityFact(comedian, peers),
    trendFact(comedian),
    tagFact(comedian),
    jokeTypeFact(comedian),
  ].filter((fact): fact is string => Boolean(fact));
}

export function getComedianIntroSummary(comedian: ComedianDetail): string {
  return `${appearanceFact(comedian)} Read jokes from each set, with stats and a breakdown of every appearance.`;
}

export function getSetIntroSummary(set: Set): string {
  const bitCount = set.bits.length;
  const beatCount = set.bits.reduce((sum, bit) => sum + bit.beats.length, 0);
  const statParts = [
    plural(bitCount, "bit"),
    plural(beatCount, "joke beat"),
    metric(set.punch_density, "punch density"),
    metric(set.tag_density, "tag density"),
  ].filter(Boolean);

  return `Watch ${set.comedian.name}'s Kill Tony episode ${set.video.number} set with a timestamped video, full transcript, and line-by-line joke breakdown. This set has ${statParts.join(", ")}.`;
}
