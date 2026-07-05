import { ATTRIBUTE_LABELS } from "@/lib/attributes";
import { JOKE_TYPE_FILTER_OPTIONS } from "@/lib/jokeTypes";

export type FilterOption = {
  value: string;
  label: string;
  param?: string;
};

export type FilterGroupConfig = {
  title: string;
  param: string;
  options: FilterOption[];
};

export type SortConfig = {
  defaultValue?: string;
  options: FilterOption[];
};

export type SearchConfig = {
  searchPath: string;
  pageSize: number;
  filters?: FilterGroupConfig[];
  sort?: SortConfig;
};

export const SET_SEARCH_CONFIG: SearchConfig = {
  searchPath: "/killtony/sets/search",
  pageSize: 20,
  filters: [
    {
      title: "Filter",
      param: "attribute",
      options: [
        { value: "bucket_pull",    label: "Bucket Pull" },
        { value: "regular",        label: "Regular" },
        { value: "golden_ticket",  label: "Golden Ticket" },
        { value: "special",        label: "Special" },
        { value: "small",  label: "Small Joke Book", param: "joke_book" },
        { value: "medium", label: "Medium Joke Book", param: "joke_book" },
        { value: "large",  label: "Big Joke Book", param: "joke_book" },
      ],
    },
  ],
  sort: {
    options: [
      { value: "bit_count",           label: "Bits" },
      { value: "punch_density",       label: "Punch density" },
      { value: "tag_density", label: "Tag density" },
    ],
  },
};

export const EPISODE_SEARCH_CONFIG: SearchConfig = {
  searchPath: "/killtony/episodes/search",
  pageSize: 20,
  sort: {
    defaultValue: "date",
    options: [
      { value: "date",             label: "Date" },
      { value: "duration",         label: "Duration" },
      { value: "set_count",        label: "Set count" },
      { value: "bucket_pulls",     label: "Bucket pulls" },
      { value: "golden_tickets",   label: "Golden tickets" },
      { value: "large_joke_books", label: "Big joke books" },
      { value: "regulars",         label: "Regulars" },
      { value: "view_count",       label: "View count" },
      { value: "like_count",       label: "Like count" },
      { value: "like_ratio",       label: "Views/like" },
    ],
  },
};

export const COMEDIAN_SEARCH_CONFIG: SearchConfig = {
  searchPath: "/killtony/comedians/search",
  pageSize: 24,
  filters: [
    {
      title: "Filter",
      param: "attribute",
      options: Object.entries(ATTRIBUTE_LABELS).map(([value, label]) => ({ value, label })),
    },
  ],
  sort: {
    options: [
      { value: "set_count",               label: "Sets" },
      { value: "avg_punch_density",       label: "Punch density" },
      { value: "avg_tag_density", label: "Tag density" },
      { value: "avg_bits_per_set",        label: "Bits per set" },
      { value: "avg_beats_per_set",       label: "Beats per set" },
    ],
  },
};

export const JOKES_SEARCH_CONFIG: SearchConfig = {
  searchPath: "/killtony/jokes/search",
  pageSize: 20,
  filters: [
    {
      title: "Filter",
      param: "joke_type",
      options: JOKE_TYPE_FILTER_OPTIONS,
    },
  ],
};
