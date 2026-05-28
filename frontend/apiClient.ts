function getCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop()?.split(";").shift() ?? null;
  return null;
}

export async function authedFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const method = (options.method ?? "GET").toUpperCase();
  const isUnsafe = !["GET", "HEAD", "OPTIONS", "TRACE"].includes(method);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (isUnsafe) {
    const csrfToken = getCookie("csrftoken");
    if (csrfToken) headers["X-CSRFToken"] = csrfToken;
  }

  let response = await fetch(url, {
    ...options,
    credentials: "include",
    headers,
  });

  if (response.status === 401) {
    const refreshRes = await fetch("/api/token/refresh/", {
      method: "POST",
      credentials: "include",
    });

    if (refreshRes.ok) {
      response = await fetch(url, {
        ...options,
        credentials: "include",
        headers,
      });
    } else {
      window.dispatchEvent(new CustomEvent("auth:expired"));
    }
  }

  return response;
}
