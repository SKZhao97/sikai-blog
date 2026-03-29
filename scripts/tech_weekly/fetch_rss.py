from __future__ import annotations

import logging
import ssl
import time
from collections.abc import Sequence
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import certifi
import feedparser
import yaml

from .config import DEFAULT_USER_AGENT, SOURCES_FILE
from .models import FeedItem, FeedSource
from .utils import clean_html_text, parse_datetime

LOGGER = logging.getLogger(__name__)


def load_sources(path: Path = SOURCES_FILE) -> list[FeedSource]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_sources = payload.get("sources", [])
    sources: list[FeedSource] = []
    for entry in raw_sources:
        sources.append(
            FeedSource(
                name=entry["name"],
                url=entry["url"],
                kind=entry.get("kind", "media"),
                topic=entry.get("topic", "tech"),
            )
        )
    return sources


def fetch_items(
    sources: Sequence[FeedSource],
    *,
    limit_sources: set[str] | None = None,
    limit_items: int | None = None,
) -> list[FeedItem]:
    items: list[FeedItem] = []
    for source in sources:
        if limit_sources and source.name not in limit_sources:
            continue
        try:
            parsed = fetch_feed(source.url)
        except Exception as exc:  # pragma: no cover - network/runtime dependent
            LOGGER.warning("Failed to fetch %s: %s", source.name, exc)
            continue
        if getattr(parsed, "bozo", 0):
            LOGGER.debug("Feedparser bozo for %s: %s", source.name, parsed.get("bozo_exception"))
        entries = parsed.entries[:limit_items] if limit_items else parsed.entries
        LOGGER.info(
            "Fetched %s entries from %s (status=%s, feed_title=%s)",
            len(entries),
            source.name,
            parsed.get("status"),
            parsed.feed.get("title"),
        )
        for entry in entries:
            published = parse_datetime(
                entry.get("published")
                or entry.get("updated")
                or entry.get("created")
                or entry.get("pubDate")
            )
            if not published:
                LOGGER.debug("Skip entry without parseable publish time from %s", source.name)
                continue
            items.append(
                FeedItem(
                    source=source.name,
                    feed_url=source.url,
                    kind=source.kind,
                    topic=source.topic,
                    title=clean_html_text(entry.get("title", "")).strip(),
                    link=entry.get("link", "").strip(),
                    guid=str(entry.get("id") or entry.get("guid") or entry.get("link") or "").strip(),
                    published_at=published,
                    summary=clean_html_text(entry.get("summary", "") or entry.get("description", "")),
                    categories=[
                        clean_html_text(str(tag.get("term", ""))).strip()
                        for tag in entry.get("tags", [])
                        if tag.get("term")
                    ],
                )
            )
    return items


def fetch_feed(url: str):
    request = Request(
        url,
        headers={
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
        },
    )
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=20, context=ssl_context) as response:
                content = response.read()
                parsed = feedparser.parse(content)
                parsed["status"] = getattr(response, "status", None)
                return parsed
        except IncompleteRead as exc:  # pragma: no cover - network/runtime dependent
            last_error = exc
            LOGGER.debug("Incomplete read for %s on attempt %s", url, attempt + 1)
        except URLError as exc:  # pragma: no cover - network/runtime dependent
            last_error = exc
            LOGGER.debug("Network error for %s on attempt %s: %s", url, attempt + 1, exc)
        time.sleep(1 + attempt)
    raise RuntimeError(f"network error: {last_error}") from last_error
