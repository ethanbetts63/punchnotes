"use client";

import { useListPageFilterRouter, ListPageFilterChipGrid } from "@/components/ListPageFilterControls";
import type { SearchConfig } from "@/lib/searchConfigs";

export default function FilterControls({ config }: { config: SearchConfig }) {
  const trackedParams = Array.from(new Set([
    ...(config.filters?.flatMap((f) => [
      f.param,
      ...f.options.map((option) => option.param).filter((param): param is string => Boolean(param)),
    ]) ?? []),
    ...(config.sort ? ["sort", "asc"] : []),
  ]));

  const { getParam, push } = useListPageFilterRouter({
    searchPath: config.searchPath,
    trackedParams,
  });

  const currentSort = getParam("sort", config.sort?.defaultValue ?? "");
  const currentAsc = getParam("asc") === "1";

  return (
    <div className="mb-6 space-y-4">
      {config.filters?.map((group) => {
        const groupParams = Array.from(new Set([
          group.param,
          ...group.options.map((option) => option.param).filter((param): param is string => Boolean(param)),
        ]));
        const hasOptionParams = group.options.some((option) => option.param);

        if (hasOptionParams) {
          const options = group.options.map((option) => ({
            ...option,
            value: `${option.param ?? group.param}:${option.value}`,
          }));
          const currentValue =
            options.find((option) => {
              const [param, value] = option.value.split(":", 2);
              return getParam(param) === value;
            })?.value ?? "";

          return (
            <ListPageFilterChipGrid
              key={group.param}
              title={group.title}
              options={options}
              currentValue={currentValue}
              onSelect={(encodedValue) => {
                const option = options.find((candidate) => candidate.value === encodedValue);
                if (!option) return;

                const [param, value] = option.value.split(":", 2);
                const isActive = getParam(param) === value;
                const overrides = Object.fromEntries(groupParams.map((groupParam) => [groupParam, ""]));
                if (!isActive) overrides[param] = value;
                push(overrides);
              }}
            />
          );
        }

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
