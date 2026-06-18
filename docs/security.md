# Security

## Repo split

Code and data live in separate git repos:

- **`punchnotes`** (public) — all application code. `pipeline/data/` is tracked and contains only `kt_ep_archive.jsonl` (everything else gitignored via `pipeline/data/.gitignore`). `pipeline/data_private/` is gitignored entirely.
- **`punchnotes_private`** (private) — cloned at `pipeline/data_private/`. Tracks `transcript_archive/`, `bit_annotated_set_archive/`, `embeddings_archive/`, `set_images_archive/`, and the comedian relationship/report JSON files.

This keeps the annotated set data (the moat) off the public repo and off the PythonAnywhere server, which only clones `punchnotes`.

Use `python manage.py archive --push` / `--pull` to sync the private repo.

## Deploy key

The private repo uses an SSH deploy key rather than a PAT so that access is scoped to a single repo and can be revoked independently.

- Private key: `~/.ssh/punchnotes_private_deploy` (never committed)
- Public key registered as a deploy key on `punchnotes_private` with write access
- SSH config alias in `~/.ssh/config`:

```
Host github-punchnotes-private
    HostName github.com
    User git
    IdentityFile ~/.ssh/punchnotes_private_deploy
```

The private repo remote is set to `git@github-punchnotes-private:ethanbetts63/punchnotes_private.git` so SSH automatically uses the deploy key.
