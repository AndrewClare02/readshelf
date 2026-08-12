# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

readshelf is a small bookmarks/reading-list API (FastAPI + SQLModel + SQLite). Save a
URL, tag it, search it; a background job fetches the page server-side and fills in the
title. A minimal same-origin static page (`app/static/index.html`) provides a UI over
the API — there is no separate frontend build.

## Commands

Run the app:
```
READSHELF_API_KEY=<any-secret> uv run uvicorn app.main:app --reload
```
Then visit `http://localhost:8000/docs` for the API, or `http://localhost:8000/` for the UI.
`READSHELF_API_KEY` is required — `app/auth.py` reads it at import time, so a missing
key fails app startup rather than the first request.

Run tests:
```
uv run pytest
```
Run a single test: `uv run pytest tests/test_bookmarks.py::test_create_and_get_bookmark`

Tests set `READSHELF_API_KEY=test-key` themselves (`tests/conftest.py`), so no env setup
is needed to run the suite.

## Architecture

- **`app/db.py`** — module-level `engine`, imported and read as `db.engine` (not
  imported by name) wherever it's used outside request handlers. This is what lets
  `tests/conftest.py` monkeypatch `db_module.engine` to point background tasks and the
  request-scoped session at the same in-memory SQLite database.
- **`app/routes/bookmarks.py`, `app/routes/tags.py`** — one `APIRouter` per resource,
  each with `dependencies=[Depends(require_api_key)]` so auth is enforced at the router
  level, not per-endpoint.
- **`app/enrichment.py`** — the background title-fetch job, scheduled via
  `BackgroundTasks` from `create_bookmark` after commit. Fetching a user-supplied URL
  server-side is an SSRF surface, so `_validate_url` resolves the hostname and rejects
  private/loopback/link-local/reserved/multicast IPs before any request is made, on top
  of a scheme allowlist, disabled redirects, a response size cap, and a content-type
  check. `_fetch_html` (the actual network call) is kept separate from
  `fetch_and_store_title` (the DB write) specifically so tests can monkeypatch just the
  network half. Any failure anywhere in the pipeline — unsafe URL, timeout, non-200,
  non-HTML, missing `<title>` — is swallowed silently and leaves `title` as `null`; this
  is deliberate, since enrichment is best-effort and must never block or error out
  bookmark creation. DNS-rebinding (TOCTOU between the validate step and the actual
  connect) is a known, accepted gap — not fixed.
- **`app/main.py`** — mounts `StaticFiles` at `/` *after* including the API routers, so
  explicit routes (`/bookmarks`, `/tags`, `/health`) are matched first and the static
  mount only catches what's left.
- **`tests/conftest.py`** — the `session` fixture monkeypatches `db.engine` (see above)
  and an autouse fixture stubs `app.enrichment._fetch_html` to return `None` for every
  test by default, so ordinary CRUD tests posting fake URLs (`https://a.com`) never make
  real network calls. Tests that need to exercise enrichment override this stub locally
  with canned HTML.
