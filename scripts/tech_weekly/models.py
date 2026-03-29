from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(slots=True)
class FeedSource:
    name: str
    url: str
    kind: str
    topic: str
    source_type: str = "rss"
    max_items: int | None = None


@dataclass(slots=True)
class FeedItem:
    source: str
    feed_url: str
    kind: str
    topic: str
    title: str
    link: str
    guid: str
    published_at: datetime
    summary: str
    categories: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EventCluster:
    event_id: str
    main_item: FeedItem
    related_items: list[FeedItem]
    score: int
    keywords: list[str]
    tags: list[str]
