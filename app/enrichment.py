import ipaddress
import re
import socket

import httpx
from sqlmodel import Session

from app import db
from app.models import Bookmark

MAX_BODY_BYTES = 1_000_000
REQUEST_TIMEOUT = 5.0
TITLE_RE = re.compile(rb"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class UnsafeURLError(Exception):
    pass


def _validate_url(url: str) -> None:
    parsed = httpx.URL(url)
    if parsed.scheme not in ("http", "https"):
        raise UnsafeURLError(f"unsupported scheme: {parsed.scheme!r}")
    if not parsed.host:
        raise UnsafeURLError("missing host")

    try:
        addrinfo = socket.getaddrinfo(parsed.host, None)
    except socket.gaierror as exc:
        raise UnsafeURLError(f"could not resolve host: {parsed.host!r}") from exc

    for family, _, _, _, sockaddr in addrinfo:
        ip = ipaddress.ip_address(sockaddr[0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise UnsafeURLError(f"unsafe resolved address: {ip}")


def _fetch_html(url: str) -> bytes | None:
    try:
        _validate_url(url)
    except UnsafeURLError:
        return None

    try:
        with httpx.Client(follow_redirects=False, timeout=REQUEST_TIMEOUT) as client:
            with client.stream("GET", url) as response:
                if response.status_code != 200:
                    return None
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    return None
                body = b""
                for chunk in response.iter_bytes():
                    body += chunk
                    if len(body) > MAX_BODY_BYTES:
                        break
                return body[:MAX_BODY_BYTES]
    except httpx.HTTPError:
        return None


def _extract_title(html: bytes) -> str | None:
    match = TITLE_RE.search(html)
    if match is None:
        return None
    title = match.group(1).decode("utf-8", errors="replace").strip()
    return title or None


def fetch_and_store_title(bookmark_id: int, url: str) -> None:
    html = _fetch_html(url)
    if html is None:
        return

    title = _extract_title(html)
    if title is None:
        return

    with Session(db.engine) as session:
        bookmark = session.get(Bookmark, bookmark_id)
        if bookmark is None:
            return
        bookmark.title = title
        session.add(bookmark)
        session.commit()
