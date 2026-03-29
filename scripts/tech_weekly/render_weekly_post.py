from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config import CONTENT_POST_DIR, MIN_EVENTS_TO_PUBLISH, TIMEZONE_NAME
from .generate_cover import generate_cover
from .models import EventCluster
from .utils import clean_title

LOGGER = logging.getLogger(__name__)
TZ = ZoneInfo(TIMEZONE_NAME)


@dataclass(slots=True)
class RenderResult:
    changed: bool
    post_path: Path | None
    cover_path: Path | None
    reason: str


def weekly_slug(target_date) -> str:
    calendar = target_date.isocalendar()
    return f"{calendar.year}-w{calendar.week:02d}-tech-weekly"


def weekly_title(target_date) -> str:
    calendar = target_date.isocalendar()
    return f"Tech Weekly | {calendar.year} W{calendar.week:02d}"


def render_weekly_post(run_at: datetime, clusters: list[EventCluster], tags: list[str], *, dry_run: bool) -> RenderResult:
    return render_weekly_post_with_options(
        run_at,
        clusters,
        tags,
        dry_run=dry_run,
        force_rewrite_date=False,
        min_events=MIN_EVENTS_TO_PUBLISH,
        force_regenerate_cover=False,
    )


def render_weekly_post_with_options(
    run_at: datetime,
    clusters: list[EventCluster],
    tags: list[str],
    *,
    dry_run: bool,
    force_rewrite_date: bool,
    min_events: int,
    force_regenerate_cover: bool,
) -> RenderResult:
    if len(clusters) < min_events:
        return RenderResult(False, None, None, "not_enough_events")

    target_date = run_at.astimezone(TZ).date()
    slug = weekly_slug(target_date)
    post_dir = CONTENT_POST_DIR / slug
    post_path = post_dir / "index.md"
    cover_path = post_dir / "cover.svg"
    target_date_str = target_date.isoformat()
    section_marker = f"## {target_date_str}"
    created = False

    existing_body = ""
    if post_path.exists():
        existing_body = post_path.read_text(encoding="utf-8")
        if section_marker in existing_body and not force_rewrite_date:
            return RenderResult(False, post_path, cover_path if cover_path.exists() else None, "section_exists")
    else:
        created = True

    front_matter = build_front_matter(run_at, target_date, tags)
    intro = (
        "This weekly post collects notable tech news from curated public RSS feeds and is updated daily.\n"
    )
    day_section = render_day_section(target_date_str, clusters)

    if created:
        new_body = front_matter + "\n" + intro + "\n" + day_section
    else:
        body_without_front_matter = strip_front_matter(existing_body)
        if force_rewrite_date:
            body_without_front_matter = remove_existing_day_section(body_without_front_matter, target_date_str)
        intro, existing_sections = split_intro_and_sections(body_without_front_matter)
        if existing_sections.strip():
            body_without_front_matter = intro.rstrip() + "\n\n" + day_section + "\n" + existing_sections.lstrip()
        else:
            body_without_front_matter = intro.rstrip() + "\n\n" + day_section
        new_body = front_matter + "\n" + body_without_front_matter + "\n"

    if dry_run:
        return RenderResult(True, post_path, cover_path, "dry_run")

    post_dir.mkdir(parents=True, exist_ok=True)
    post_path.write_text(new_body, encoding="utf-8")
    generate_cover(
        cover_path,
        target_date=target_date,
        primary_tag=tags[2] if len(tags) > 2 else "default",
        force=force_regenerate_cover,
    )
    return RenderResult(True, post_path, cover_path, "created" if created else "updated")


def build_front_matter(run_at: datetime, target_date, tags: list[str]) -> str:
    title = weekly_title(target_date)
    date_value = run_at.astimezone(TZ).strftime("%Y-%m-%dT%H:%M:%S%z")
    date_value = f"{date_value[:-2]}:{date_value[-2:]}"
    serialized_tags = ", ".join(f"'{tag}'" for tag in tags)
    return "\n".join(
        [
            "+++",
            f"date = '{date_value}'",
            "draft = false",
            f"title = '{title}'",
            f"description = '{title} generated from curated public RSS feeds.'",
            "categories = ['Tech Digest']",
            f"tags = [{serialized_tags}]",
            "image = 'cover.svg'",
            "+++",
        ]
    )


def strip_front_matter(content: str) -> str:
    match = re.match(r"^\+\+\+\n.*?\n\+\+\+\n?", content, flags=re.DOTALL)
    if not match:
        return content
    return content[match.end() :]


def remove_existing_day_section(content: str, date_string: str) -> str:
    pattern = rf"\n## {re.escape(date_string)}\n.*?(?=\n## \d{{4}}-\d{{2}}-\d{{2}}\n|\Z)"
    updated = re.sub(pattern, "\n", "\n" + content.strip() + "\n", flags=re.DOTALL)
    return updated.strip() + "\n"


def split_intro_and_sections(content: str) -> tuple[str, str]:
    match = re.search(r"^## \d{4}-\d{2}-\d{2}$", content, flags=re.MULTILINE)
    if not match:
        return content.strip(), ""
    return content[: match.start()].rstrip(), content[match.start() :].lstrip()


def render_day_section(date_string: str, clusters: list[EventCluster]) -> str:
    blocks = [f"## {date_string}"]
    for cluster in clusters:
        title = clean_title(cluster.main_item.title)
        summary = cluster.main_item.summary.strip() or "See the source link for the full update."
        published_at = cluster.main_item.published_at.astimezone(TZ).strftime("%Y-%m-%d %H:%M GMT+8")
        blocks.extend(
            [
                "",
                f"### {title}",
                "",
                f"Source: {cluster.main_item.source}",
                f"Published: {published_at}",
                "",
                "**English Summary:**",
                summary,
                "",
                "Link:",
                cluster.main_item.link,
            ]
        )
        if cluster.related_items:
            blocks.extend(["", "Related:"])
            for item in cluster.related_items:
                blocks.append(item.link)
    return "\n".join(blocks).rstrip() + "\n"
