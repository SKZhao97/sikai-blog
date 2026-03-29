from __future__ import annotations

import hashlib
import html
import logging
import re
from datetime import datetime, time, timedelta
from typing import Iterable
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .config import (
    ACTION_KEYWORDS,
    IMPORTANT_KEYWORDS,
    STOPWORDS,
    TAG_RULES,
    TIMEZONE_NAME,
    WEAK_TITLE_TERMS,
)

LOGGER = logging.getLogger(__name__)
TZ = ZoneInfo(TIMEZONE_NAME)


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = date_parser.parse(value)
    except (ValueError, TypeError, OverflowError) as exc:
        LOGGER.debug("Failed to parse datetime %r: %s", value, exc)
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=TZ)
    return parsed.astimezone(TZ)


def rolling_window_0830(run_at: datetime | None) -> tuple[datetime, datetime, datetime]:
    current = run_at.astimezone(TZ) if run_at else datetime.now(TZ)
    anchor = datetime.combine(current.date(), time(hour=8, minute=30), tzinfo=TZ)
    if current < anchor:
        end = anchor
    else:
        end = anchor
    start = end - timedelta(days=1)
    return current, start, end


def clean_html_text(value: str) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    text = soup.get_text(" ", strip=True)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def trim_summary(value: str, *, limit: int = 260) -> str:
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s-]", " ", title)
    parts = [part for part in re.split(r"\s+", title) if part and part not in WEAK_TITLE_TERMS]
    return " ".join(parts)


def tokenize(text: str) -> list[str]:
    normalized = normalize_title(text)
    return [token for token in normalized.split() if token and token not in STOPWORDS]


def extract_keywords(*values: str) -> list[str]:
    seen: set[str] = set()
    keywords: list[str] = []
    for value in values:
        for token in tokenize(value):
            if len(token) < 3:
                continue
            if token not in seen:
                seen.add(token)
                keywords.append(token)
    return keywords


def detect_tags(texts: Iterable[str]) -> list[str]:
    combined = " ".join(texts).lower()
    tags: list[str] = []
    for tag, keywords in TAG_RULES.items():
        if any(keyword in combined for keyword in keywords):
            tags.append(tag)
    return tags


def jaccard_similarity(left: Iterable[str], right: Iterable[str]) -> float:
    left_set = set(left)
    right_set = set(right)
    if not left_set or not right_set:
        return 0.0
    intersection = len(left_set & right_set)
    union = len(left_set | right_set)
    return intersection / union


def build_event_id(title: str, link: str) -> str:
    normalized = normalize_title(title)
    host = urlparse(link).netloc
    digest = hashlib.sha1(f"{host}:{normalized}".encode("utf-8")).hexdigest()
    return digest[:12]


def score_keywords(tokens: Iterable[str]) -> int:
    return sum(1 for token in tokens if token in IMPORTANT_KEYWORDS)


def has_action_keyword(tokens: Iterable[str]) -> bool:
    token_set = set(tokens)
    return any(keyword in token_set for keyword in ACTION_KEYWORDS)


def ensure_bilingual_title(title: str) -> tuple[str, str]:
    english = clean_title(title)
    chinese = translate_title(english)
    return chinese, english


def clean_title(title: str) -> str:
    return re.sub(r"\s+", " ", clean_html_text(title)).strip()


def translate_title(title: str) -> str:
    patterns = [
        (r"^(?P<subject>.+?) launches (?P<object>.+)$", "{subject}推出{object}"),
        (r"^(?P<subject>.+?) launched (?P<object>.+)$", "{subject}推出{object}"),
        (r"^(?P<subject>.+?) introduces (?P<object>.+)$", "{subject}推出{object}"),
        (r"^(?P<subject>.+?) introduced (?P<object>.+)$", "{subject}推出{object}"),
        (r"^(?P<subject>.+?) releases (?P<object>.+)$", "{subject}发布{object}"),
        (r"^(?P<subject>.+?) released (?P<object>.+)$", "{subject}发布{object}"),
        (r"^(?P<subject>.+?) announces (?P<object>.+)$", "{subject}宣布{object}"),
        (r"^(?P<subject>.+?) announced (?P<object>.+)$", "{subject}宣布{object}"),
        (r"^(?P<subject>.+?) updates (?P<object>.+)$", "{subject}更新{object}"),
        (r"^(?P<subject>.+?) upgrades (?P<object>.+)$", "{subject}升级{object}"),
        (r"^(?P<subject>.+?) acquires (?P<object>.+)$", "{subject}收购{object}"),
        (r"^(?P<subject>.+?) acquired (?P<object>.+)$", "{subject}收购{object}"),
        (r"^(?P<subject>.+?) study outlines (?P<object>.+)$", "{subject}研究指出{object}"),
    ]
    lowered = clean_title(title).lower()
    for pattern, template in patterns:
        match = re.match(pattern, lowered)
        if match:
            subject = restore_case_fragment(title, match.group("subject"))
            obj = restore_case_fragment(title, match.group("object"))
            return compact_mixed_language(template.format(subject=subject, object=obj))
    return f"关于《{clean_title(title)}》的报道"


def restore_case_fragment(original: str, fragment: str) -> str:
    lowered_original = original.lower()
    start = lowered_original.find(fragment.lower())
    if start == -1:
        return fragment.strip()
    end = start + len(fragment)
    return original[start:end].strip()


def compact_mixed_language(value: str) -> str:
    value = value.replace(" ai ", " AI ").replace(" Ai ", " AI ")
    value = value.replace(" api ", " API ").replace(" Api ", " API ")
    value = re.sub(r"\s+", " ", value).strip(" ,.-")
    return value


def build_bilingual_summaries(summary: str, title: str, source: str, tags: list[str]) -> tuple[str, str]:
    english = trim_summary(clean_html_text(summary) or clean_title(title))
    zh_title = translate_title(title)
    tag_text = "、".join(tags[:3]) if tags else "科技"
    chinese = (
        f"这则报道来自 {source}，主题主要涉及{tag_text}。"
        f" 标题显示，{zh_title}。"
        " 具体细节可结合英文摘要与原文继续阅读。"
    )
    chinese = trim_summary(compact_mixed_language(chinese), limit=140)
    return chinese, english
