from __future__ import annotations

import logging
from collections import Counter
from collections.abc import Iterable
from urllib.parse import urlparse

from .config import (
    DEFAULT_MAX_EVENTS,
    EXCLUDED_SUBSTRINGS,
    FIXED_TAGS,
    MAX_DYNAMIC_TAGS,
    MIN_EVENTS_TO_PUBLISH,
    NOISY_TITLE_KEYWORDS,
    WEAK_NEWS_KEYWORDS,
)
from .models import EventCluster, FeedItem
from .utils import (
    build_event_id,
    detect_tags,
    extract_keywords,
    has_action_keyword,
    jaccard_similarity,
    normalize_title,
    score_keywords,
)

LOGGER = logging.getLogger(__name__)


def filter_items(items: Iterable[FeedItem], *, start, end) -> list[FeedItem]:
    filtered: list[FeedItem] = []
    reason_counts: Counter[str] = Counter()
    for item in items:
        if not item.link or any(part in item.link.lower() for part in EXCLUDED_SUBSTRINGS):
            reason_counts["excluded_link"] += 1
            continue
        if not (start <= item.published_at < end):
            reason_counts["outside_window"] += 1
            continue
        lowered_title = item.title.lower()
        if any(keyword in lowered_title for keyword in NOISY_TITLE_KEYWORDS):
            reason_counts["noisy_title"] += 1
            continue
        if any(keyword in lowered_title for keyword in WEAK_NEWS_KEYWORDS):
            reason_counts["weak_news"] += 1
            continue
        if len(item.title.strip()) < 12:
            reason_counts["short_title"] += 1
            continue
        filtered.append(item)
    LOGGER.info("Filtered down to %s items inside target window", len(filtered))
    if reason_counts:
        LOGGER.info("Filter drop reasons: %s", dict(reason_counts))
    return filtered


def dedupe_items(items: Iterable[FeedItem]) -> list[FeedItem]:
    deduped: list[FeedItem] = []
    seen_links: set[str] = set()
    seen_guids: set[str] = set()
    seen_titles: set[str] = set()
    for item in items:
        normalized_link = item.link.rstrip("/")
        normalized_guid = item.guid.strip()
        normalized = normalize_title(item.title)
        if normalized_link and normalized_link in seen_links:
            continue
        if normalized_guid and normalized_guid in seen_guids:
            continue
        if normalized and normalized in seen_titles:
            continue
        if normalized_link:
            seen_links.add(normalized_link)
        if normalized_guid:
            seen_guids.add(normalized_guid)
        if normalized:
            seen_titles.add(normalized)
        deduped.append(item)
    LOGGER.info("Deduped to %s unique items", len(deduped))
    return deduped


def cluster_items(items: list[FeedItem], *, max_events: int = DEFAULT_MAX_EVENTS) -> list[EventCluster]:
    clusters: list[dict] = []
    for item in sorted(items, key=lambda current: current.published_at, reverse=True):
        tokens = set(extract_keywords(item.title, item.summary))
        matched = None
        for cluster in clusters:
            similarity = jaccard_similarity(tokens, cluster["tokens"])
            same_source_host = urlparse(item.link).netloc == urlparse(cluster["main_item"].link).netloc
            if similarity >= 0.55 or (similarity >= 0.35 and not same_source_host):
                matched = cluster
                break
        if matched:
            matched["items"].append(item)
            matched["tokens"].update(tokens)
        else:
            clusters.append({"main_item": item, "items": [item], "tokens": set(tokens)})

    result: list[EventCluster] = []
    for cluster in clusters:
        main_item = choose_main_item(cluster["items"])
        keywords = extract_keywords(main_item.title, main_item.summary)[:8]
        tags = detect_tags([main_item.title, main_item.summary, " ".join(keywords)])
        score = score_cluster(cluster["items"], keywords, main_item, tags)
        result.append(
            EventCluster(
                event_id=build_event_id(main_item.title, main_item.link),
                main_item=main_item,
                related_items=[item for item in cluster["items"] if item.link != main_item.link][:3],
                score=score,
                keywords=keywords,
                tags=tags,
            )
        )
    result.sort(key=lambda cluster: (cluster.score, cluster.main_item.published_at), reverse=True)
    return result[:max_events]


def choose_main_item(items: list[FeedItem]) -> FeedItem:
    return max(
        items,
        key=lambda item: (
            2 if item.kind == "official" else 1,
            len(item.summary),
            item.published_at.timestamp(),
        ),
    )


def score_cluster(items: list[FeedItem], keywords: list[str], main_item: FeedItem, tags: list[str]) -> int:
    score = 0
    score += 5 if main_item.kind == "official" else 3
    score += 2 * max(0, len(items) - 1)
    score += score_keywords(keywords) * 2
    score += 2 if has_action_keyword(keywords) else 0
    score += len(tags)
    return score


def compute_weekly_tags(clusters: Iterable[EventCluster]) -> list[str]:
    counts: Counter[str] = Counter()
    for cluster in clusters:
        counts.update(cluster.tags)
    dynamic = [tag for tag, _count in counts.most_common(MAX_DYNAMIC_TAGS)]
    return FIXED_TAGS + dynamic
