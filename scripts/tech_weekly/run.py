from __future__ import annotations

import argparse
import logging
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate or update the weekly tech digest.")
    parser.add_argument("--run-at", help="ISO datetime to simulate the run time, e.g. 2026-03-30T08:30:00+08:00")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline without writing files")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debug logging")
    parser.add_argument("--limit-sources", help="Comma-separated source names to include")
    parser.add_argument("--limit-items", type=int, help="Limit items fetched per RSS feed")
    parser.add_argument("--max-events", type=int, default=None, help="Limit number of rendered events")
    parser.add_argument("--min-events", type=int, default=None, help="Override minimum event threshold for rendering")
    parser.add_argument("--force-regenerate-cover", action="store_true", help="Regenerate cover.svg even if it already exists")
    parser.add_argument(
        "--force-rewrite-date",
        action="store_true",
        help="Rewrite the existing section for the target date instead of skipping it",
    )
    return parser.parse_args()


def configure_logging(debug: bool) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def main() -> int:
    args = parse_args()
    configure_logging(args.debug)

    from .config import MIN_EVENTS_TO_PUBLISH
    from .fetch_rss import fetch_items, load_sources
    from .filter_and_cluster import cluster_items, compute_weekly_tags, dedupe_items, filter_items
    from .render_weekly_post import render_weekly_post_with_options
    from .utils import parse_datetime, rolling_window_0830

    run_at = parse_datetime(args.run_at) if args.run_at else None
    current, start, end = rolling_window_0830(run_at)
    logging.info("Run time: %s", current.isoformat())
    logging.info("Window: %s <= published_at < %s", start.isoformat(), end.isoformat())

    limit_sources = None
    if args.limit_sources:
        limit_sources = {part.strip() for part in args.limit_sources.split(",") if part.strip()}

    sources = load_sources()
    logging.info("Loaded %s RSS sources", len(sources))
    raw_items = fetch_items(sources, limit_sources=limit_sources, limit_items=args.limit_items)
    filtered_items = filter_items(raw_items, start=start, end=end)
    deduped_items = dedupe_items(filtered_items)
    clusters = cluster_items(deduped_items, max_events=args.max_events or 8)
    tags = compute_weekly_tags(clusters)
    min_events = args.min_events if args.min_events is not None else MIN_EVENTS_TO_PUBLISH

    logging.info("Clusters selected: %s", len(clusters))
    if len(clusters) < min_events:
        logging.info("Only %s clusters remain, below publish threshold %s", len(clusters), min_events)
    for cluster in clusters:
        logging.info(
            "Event score=%s source=%s title=%s",
            cluster.score,
            cluster.main_item.source,
            cluster.main_item.title,
        )

    result = render_weekly_post_with_options(
        current,
        clusters,
        tags,
        dry_run=args.dry_run,
        force_rewrite_date=args.force_rewrite_date,
        min_events=min_events,
        force_regenerate_cover=args.force_regenerate_cover,
    )
    logging.info("Render result: %s", result.reason)
    if result.post_path:
        logging.info("Post path: %s", result.post_path)
    if result.cover_path:
        logging.info("Cover path: %s", result.cover_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
