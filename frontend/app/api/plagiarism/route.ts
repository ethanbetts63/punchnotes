const API_BASE_URL = process.env.DJANGO_API_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  const body = await request.json();
  const res = await fetch(`${API_BASE_URL}/api/killtony/plagiarism/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const contentType = res.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    const text = await res.text();
    console.error("[plagiarism proxy] non-JSON response from Django:", res.status, text.slice(0, 200));
    return Response.json({ error: `Upstream error (${res.status})` }, { status: 502 });
  }
  const data = await res.json();
  return Response.json(data, { status: res.status });
}
