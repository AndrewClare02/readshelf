import app.enrichment as enrichment_module
from app.enrichment import UnsafeURLError, _extract_title, _validate_url, fetch_and_store_title
from app.models import Bookmark


def test_extract_title_normal():
    html = b"<html><head><title>Hello World</title></head></html>"
    assert _extract_title(html) == "Hello World"


def test_extract_title_missing():
    html = b"<html><head></head><body>no title here</body></html>"
    assert _extract_title(html) is None


def test_extract_title_empty_or_whitespace():
    assert _extract_title(b"<title></title>") is None
    assert _extract_title(b"<title>   \n  </title>") is None


def test_validate_url_rejects_non_http_scheme():
    try:
        _validate_url("file:///etc/passwd")
        assert False, "expected UnsafeURLError"
    except UnsafeURLError:
        pass


def test_validate_url_rejects_loopback():
    try:
        _validate_url("http://127.0.0.1/")
        assert False, "expected UnsafeURLError"
    except UnsafeURLError:
        pass


def test_validate_url_rejects_link_local_metadata_address():
    try:
        _validate_url("http://169.254.169.254/")
        assert False, "expected UnsafeURLError"
    except UnsafeURLError:
        pass


def test_fetch_and_store_title_writes_title(client, session, auth_headers, monkeypatch):
    html = b"<html><head><title>Canned Title</title></head></html>"
    monkeypatch.setattr(enrichment_module, "_fetch_html", lambda url: html)

    response = client.post("/bookmarks", json={"url": "https://a.com"}, headers=auth_headers)
    assert response.status_code == 201
    bookmark_id = response.json()["id"]

    fetch_and_store_title(bookmark_id, "https://a.com")

    stored = session.get(Bookmark, bookmark_id)
    session.refresh(stored)
    assert stored.title == "Canned Title"
