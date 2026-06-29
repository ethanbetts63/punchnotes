export const ATTRIBUTE_LABELS: Record<string, string> = {
  bucket_pull: "Bucket Pull",
  regular: "Regular",
  golden_ticket: "Golden Ticket",
  special: "Special",
  gay: "Gay",
  lesbian: "Lesbian",
  bisexual: "Bisexual",
  man: "Man",
  woman: "Woman",
  trans: "Trans",
  white: "White",
  black: "Black",
  asian: "Asian",
  latino: "Latino",
  middle_eastern: "Middle Eastern",
  disabled: "Disabled",
  old: "Old",
  young: "Young",
  "middle-age": "Middle-Age",
};

export function formatAttributeLabels(attributes: string[]): string | undefined {
  const labels = attributes
    .filter((attr) => attr in ATTRIBUTE_LABELS)
    .map((attr) => ATTRIBUTE_LABELS[attr]);
  return labels.length > 0 ? labels.join(" / ") : undefined;
}
