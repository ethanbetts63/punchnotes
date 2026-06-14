"use client";

import { useListPageFilterRouter, ListPageFilterChipGrid } from "@/components/ListPageFilterControls";
import type { SearchConfig } from "@/lib/searchConfigs";

export default function FilterControls({ config }: { config: SearchConfig }) {
  const trackedParams = [
    ...(config.filters?.map((f) => f.param) ?? []),
    ...(config.sort ? ["sort", "asc"] : []),
  ];

  const { getParam, push } = useListPageFilterRouter({
    searchPath: config.searchPath,
    trackedParams,
  });

  const currentSort = getParam("sort", config.sort?.defaultValue ?? "");
  const currentAsc = getParam("asc") === "1";

  return (
    <div className="mb-6 space-y-4">
      {config.filters?.map((group) => {
        const current = getParam(group.param);
        return (
          <ListPageFilterChipGrid
            key={group.param}
            title={group.title}
            options={group.options}
            currentValue={current}
            onSelect={(value) => push({ [group.param]: current === value ? "" : value })}
          />
        );
      })}

      {config.sort && (
        <ListPageFilterChipGrid
          title="Sort"
          options={config.sort.options}
          currentValue={currentSort}
          currentAsc={currentAsc}
          onToggleAsc={() => push({ asc: currentAsc ? "" : "1" })}
          onSelect={(value) => push({ sort: currentSort === value ? "" : value })}
        />
      )}
    </div>
  );
}
