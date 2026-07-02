import type { ComedianDetail, Set } from "@/lib/serverApi";
import { fmt2 } from "@/lib/killTonyDisplay";

function plural(count: number, singular: string, pluralForm = `${singular}s`) {
  return `${count} ${count === 1 ? singular : pluralForm}`;
}

function metric(value: number | null, label: string) {
  return value == null ? null : `${fmt2(value)} ${label}`;
}

export function getComedianIntroSummary(comedian: ComedianDetail): string {
  const statParts = [
    metric(comedian.avg_bits_per_set, "bits"),
    metric(comedian.avg_beats_per_set, "beats"),
    metric(comedian.avg_punch_density, "punch density"),
    metric(comedian.avg_tag_density, "tag density"),
  ].filter(Boolean);

  const statsSentence = statParts.length
    ? ` Across ${plural(comedian.set_count, "indexed set")}, ${comedian.name} averages ${statParts.join(", ")} per set.`
    : ` Across ${plural(comedian.set_count, "indexed set")}, PunchNotes tracks ${comedian.name}'s set history in the archive.`;

  return `See every ${comedian.name} Kill Tony set on PunchNotes, with timestamped videos, transcripts, and joke breakdowns.${statsSentence}`;
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
