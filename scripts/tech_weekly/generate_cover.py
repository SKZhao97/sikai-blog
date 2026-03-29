from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path

from .config import PRIMARY_TAG_COLORS


def iso_week_date_range(target_date: date) -> tuple[str, str]:
    monday = target_date - timedelta(days=target_date.weekday())
    sunday = monday + timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()


def build_cover_svg(*, title: str, week_label: str, date_range: str, primary_tag: str) -> str:
    dark, mid, light = PRIMARY_TAG_COLORS.get(primary_tag, PRIMARY_TAG_COLORS["default"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="640" viewBox="0 0 1600 640" fill="none">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1600" y2="640" gradientUnits="userSpaceOnUse">
      <stop stop-color="{dark}"/>
      <stop offset="1" stop-color="{mid}"/>
    </linearGradient>
  </defs>
  <rect width="1600" height="640" fill="url(#bg)"/>
  <circle cx="1290" cy="140" r="180" fill="{light}" fill-opacity="0.18"/>
  <circle cx="1420" cy="520" r="240" fill="{light}" fill-opacity="0.10"/>
  <rect x="110" y="92" width="420" height="10" rx="5" fill="{light}" fill-opacity="0.82"/>
  <text x="110" y="220" fill="white" font-family="Georgia, 'Times New Roman', serif" font-size="78" font-weight="700">{title}</text>
  <text x="110" y="306" fill="white" font-family="Georgia, 'Times New Roman', serif" font-size="60" font-weight="500">Tech Weekly</text>
  <text x="110" y="420" fill="{light}" font-family="Arial, sans-serif" font-size="38" font-weight="700">{week_label}</text>
  <text x="110" y="478" fill="{light}" font-family="Arial, sans-serif" font-size="30">{date_range}</text>
  <text x="110" y="568" fill="white" font-family="Arial, sans-serif" font-size="24" opacity="0.9">Generated automatically from curated public RSS feeds</text>
</svg>
"""


def generate_cover(path: Path, *, target_date: date, primary_tag: str) -> None:
    if path.exists():
        return
    week_label = f"{target_date.isocalendar().year} W{target_date.isocalendar().week:02d}"
    start, end = iso_week_date_range(target_date)
    svg = build_cover_svg(
        title="Tech Weekly",
        week_label=week_label,
        date_range=f"{start} to {end}",
        primary_tag=primary_tag,
    )
    path.write_text(svg, encoding="utf-8")
