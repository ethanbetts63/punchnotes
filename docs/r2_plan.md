# Comedian Image Storage — Cloudflare R2 Plan

## Goal
Display a headshot/frame of each comedian on their detail page, sourced from their YouTube appearance at `start_seconds`.

## Data we already have
- `Episode.video_id` — the YouTube video ID
- `Set.start_seconds` — exact timestamp the comedian appears

## What we need to build

### 1. DB field
Add `image_url` (nullable CharField/URLField) to the `Comedian` model.

### 2. Pipeline step: frame extraction
New management command (e.g. `extract_comedian_images`):
- For each comedian missing an `image_url`, find their earliest Set
- Use `yt-dlp --download-sections` to grab ~2s of video around `start_seconds`
- Use `ffmpeg` to extract one frame as a JPEG
- Upload to R2 via `boto3` (S3-compatible, point at R2 endpoint)
- Save the R2 public URL back to `comedian.image_url`

### 3. R2 bucket config
- Create a public bucket (or use a public access policy)
- Note the bucket endpoint URL and store credentials in `.env`
- Install `boto3` in the pipeline environment

### 4. API
Expose `image_url` in the comedian serializer so the frontend receives it.

### 5. Frontend
Replace the initials placeholder in `app/killtony/comedians/[slug]/page.tsx`
with `<Image src={comedian.image_url} />` (Next.js Image component).
Whitelist the R2 domain in `next.config.js`.

## Notes
- `yt-dlp` and `ffmpeg` must be available on PythonAnywhere
- Each image only needs to be extracted once; re-run the command as new episodes are imported
- Next.js Image handles WebP conversion, resizing, and CDN caching on Vercel's edge
