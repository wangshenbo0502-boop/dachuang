"""Allowlisted RSS discovery. Publication time is never inferred from retrieval time."""
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from hashlib import sha256
from html.parser import HTMLParser
from threading import Lock
from time import monotonic
from urllib.parse import urlparse
from xml.etree import ElementTree

import httpx


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def parse_feed(payload: bytes, source: str, host: str) -> list[dict]:
    if len(payload) > 2_000_000 or b"<!DOCTYPE" in payload.upper() or b"<!ENTITY" in payload.upper():
        raise ValueError("Unsupported feed")
    root = ElementTree.fromstring(payload)
    now = datetime.now(timezone.utc)
    items = []
    for node in root.findall("./channel/item")[:40]:
        url = (node.findtext("link") or "").strip()
        parsed = urlparse(url)
        if parsed.scheme != "https" or not (parsed.hostname == host or (parsed.hostname or "").endswith("." + host)):
            continue
        try:
            published = parsedate_to_datetime(node.findtext("pubDate") or "").astimezone(timezone.utc)
        except (ValueError, TypeError, OverflowError):
            continue
        if published > now or published < now - timedelta(days=30):
            continue
        text = PlainText()
        text.feed(node.findtext("description") or "")
        items.append({
            "doc_id": sha256(url.encode()).hexdigest(),
            "title": node.findtext("title") or source,
            "content": " ".join(text.parts).strip()[:1000],
            "category": "market",
            "source": source,
            "metadata": {
                "source_url": url, "source_name": source,
                "published_at": published.isoformat(), "content_type": "行业资讯",
                "recommendation": "官方技术动态，可用于了解开发工具和工程实践变化",
            },
        })
    return items


class InsightService:
    sources = [
        ("GitHub 官方博客", "https://github.blog/feed/", "github.blog"),
        ("Python 官方博客", "https://blog.python.org/feeds/posts/default?alt=rss", "python.org"),
    ]
    _lock = Lock()
    _cached: dict | None = None
    _expires = 0.0

    @classmethod
    def feed(cls) -> dict:
        with cls._lock:
            if cls._cached is not None and monotonic() < cls._expires:
                return cls._cached
            items, unavailable = [], []
            with httpx.Client(timeout=6, follow_redirects=False) as client:
                for name, url, host in cls.sources:
                    try:
                        with client.stream("GET", url, headers={"User-Agent": "ITCareerResources/1.0"}) as response:
                            response.raise_for_status()
                            payload = bytearray()
                            for chunk in response.iter_bytes():
                                payload.extend(chunk)
                                if len(payload) > 2_000_000:
                                    raise ValueError("Feed too large")
                            items.extend(parse_feed(bytes(payload), name, host))
                    except (httpx.HTTPError, ValueError, ElementTree.ParseError):
                        unavailable.append(name)
            items.sort(key=lambda item: item["metadata"]["published_at"], reverse=True)
            cls._cached = {
                "items": items[:18], "unavailable_sources": unavailable,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "period_days": 30,
            }
            cls._expires = monotonic() + (900 if items else 60)
            return cls._cached
