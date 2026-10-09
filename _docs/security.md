# Security

PunchNotes is split into a mostly public Next.js frontend and a Django REST API. The public site exposes Kill Tony catalogue pages, set transcripts, joke metadata, search, and the similarity checker. Pipeline ingestion and update endpoints are private backend tooling.

## Data Boundary

Code and data live in separate git repos:

- `punchnotes` is the public application repo. `pipeline/data/` is tracked and contains only public or low-sensitivity pipeline data. `pipeline/data_private/` is gitignored entirely.
- `punchnotes_private` is cloned at `pipeline/data_private/` and holds transcript archives, annotated set archives, embedding archives, and comedian relationship/report JSON files.

This keeps the annotated set data off the public repo and off the production app server unless explicitly synced. Use `python manage.py archive --push` and `python manage.py archive --pull` to sync the private repo.

## Deploy Key

The private repo uses an SSH deploy key rather than a personal access token so access is scoped to a single repo and can be revoked independently.

- Private key: `~/.ssh/punchnotes_private_deploy`, never committed.
- Public key: registered as a deploy key on `punchnotes_private` with write access.
- Private repo remote: `git@github-punchnotes-private:ethanbetts63/punchnotes_private.git`.

The SSH config alias should point GitHub access for that private repo at the deploy key:

```text
Host github-punchnotes-private
    HostName github.com
    User git
    IdentityFile ~/.ssh/punchnotes_private_deploy
```

## Frontend Boundary

The public frontend is served by Next.js. API requests can be proxied through the frontend rewrite in `frontend/next.config.ts`:

```text
/api/:path* -> DJANGO_API_URL/api/:path*/
```

This keeps browser requests on the frontend origin while Django remains responsible for API permissions, request validation, and throttling.

## Security Headers

The frontend sets baseline browser security headers in `frontend/next.config.ts`:

| Header | Value |
|---|---|
| `X-Frame-Options` | `DENY` |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=()` |

The Django API sets `Cache-Control: no-store` on `/api/` responses via `config.middleware.NoCacheApiMiddleware`.

## API Permissions

DRF defaults to authenticated access:

```text
DEFAULT_PERMISSION_CLASSES = IsAuthenticated
```

Public catalogue and search endpoints explicitly opt out with `AllowAny`:

- `GET /api/killtony/episodes/`
- `GET /api/killtony/episodes/{slug}/`
- `GET /api/killtony/comedians/`
- `GET /api/killtony/comedians/{slug}/`
- `GET /api/killtony/sets/`
- `GET /api/killtony/sets/{slug}/`
- `GET /api/killtony/jokes/`
- `GET /api/killtony/bits/`
- `GET /api/killtony/search/`
- `POST /api/killtony/plagiarism/`

This keeps the intended public surface public while making newly added API views private unless they deliberately opt out.

## Throttling

DRF throttling is enabled globally for anonymous and authenticated callers, plus scoped throttles for higher-risk endpoint groups.

Current default rates are environment-overridable:

| Scope | Default |
|---|---:|
| `anon` | `300/hour` |
| `user` | `2000/hour` |
| `catalogue` | `120/min` |
| `search` | `60/min` |
| `plagiarism` | `10/hour` |
| `pipeline` | `120/min` |

The plagiarism/similarity endpoint is throttled separately because it can call HuggingFace and run vector similarity work.

## Similarity Checker

`POST /api/killtony/plagiarism/` is public but constrained:

- Request `text` must be a string.
- Request `text` is capped at 2,000 characters.
- Results are cached under a SHA-256 cache key rather than raw text.
- Plagiarism and embedding cache entries expire after seven days.
- The endpoint has its own `plagiarism` throttle scope.

## Pipeline API

Pipeline endpoints live under `/api/pipeline/` and require:

```text
Authorization: Bearer <PIPELINE_API_KEY>
```

`PipelineKeyPermission` uses constant-time comparison for the bearer token. Pipeline views do not use session or JWT authentication; the bearer key is the access-control boundary for local ingestion, scraping, image, and embedding workflows.

## CSRF And CORS

CSRF middleware is enabled. CORS and CSRF trusted origins are restricted to configured frontend origins:

- `LOCAL_FRONTEND_URL`
- `PRODUCTION_FRONTEND_URL`, when set

PunchNotes does not currently use cookie-based API authentication for public browser flows, so CSRF is mostly relevant for future authenticated browser endpoints and Django admin behavior.

## Production Settings

Production-oriented security settings are configured from environment variables with secure defaults when `DEBUG=False`:

- `SECURE_SSL_REDIRECT`
- `SECURE_PROXY_SSL_HEADER`, when `TRUST_X_FORWARDED_PROTO` is enabled
- `SECURE_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SESSION_COOKIE_HTTPONLY`
- `X_FRAME_OPTIONS = DENY`

## Known Issues

Public list endpoints are still unpaginated at the API layer. The frontend paginates after fetching list payloads, which is simple but leaves catalogue/search endpoints more scrapeable and potentially heavier than necessary as the dataset grows.

The similarity checker remains public. Throttling, validation, and finite caching reduce abuse risk, but it can still spend external embedding quota. If abuse appears, require a server-issued token, login, turnstile-style challenge, or move the feature behind a waitlist/admin-only flow.
