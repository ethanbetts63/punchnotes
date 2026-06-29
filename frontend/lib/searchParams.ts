export function parseSearchPageParams(params: Record<string, string>) {
  return {
    query: (params.q ?? "").trim(),
    page: Math.max(1, parseInt(params.page ?? "1", 10) || 1),
    queryString: new URLSearchParams(params).toString(),
  };
}
