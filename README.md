# readshelf

A small bookmarks/reading-list API. Save a URL, tag it, search it; a background job
fills in the page title for you.

## Run it

```
uv run uvicorn app.main:app --reload
```

Then visit `http://localhost:8000/docs`.

## Test it

```
uv run pytest
```
