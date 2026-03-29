from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_DIR = Path(__file__).resolve().parent
CONTENT_POST_DIR = REPO_ROOT / "content" / "post"
SOURCES_FILE = SCRIPT_DIR / "sources.yaml"
TIMEZONE_NAME = "Asia/Shanghai"
FIXED_TAGS = ["Tech News", "Weekly"]
MAX_DYNAMIC_TAGS = 4
MIN_EVENTS_TO_PUBLISH = 3
DEFAULT_MAX_EVENTS = 8
DEFAULT_USER_AGENT = "tech-weekly-bot/1.0 (+https://www.sikaizhao.com/)"

# Tags are kept broad on purpose to avoid noisy weekly metadata.
TAG_RULES = {
    "AI": [
        "openai",
        "anthropic",
        "gpt",
        "llm",
        "gemini",
        "deepmind",
        "claude",
        "model",
        "chatgpt",
    ],
    "Developer Tools": [
        "github",
        "vscode",
        "sdk",
        "cli",
        "copilot",
        "api",
        "developer",
    ],
    "Cloud": [
        "aws",
        "cloudflare",
        "gcp",
        "azure",
        "kubernetes",
        "serverless",
        "cloud",
    ],
    "Open Source": [
        "open source",
        "apache",
        "linux foundation",
        "github repo",
        "repository",
    ],
    "Security": [
        "security",
        "vulnerability",
        "breach",
        "cve",
        "attack",
        "patch",
    ],
}

PRIMARY_TAG_COLORS = {
    "AI": ("#0f766e", "#14b8a6", "#99f6e4"),
    "Cloud": ("#1d4ed8", "#3b82f6", "#bfdbfe"),
    "Security": ("#155e75", "#06b6d4", "#bae6fd"),
    "Open Source": ("#0f766e", "#2dd4bf", "#99f6e4"),
    "Developer Tools": ("#1d4ed8", "#38bdf8", "#bae6fd"),
    "default": ("#0f766e", "#0891b2", "#bae6fd"),
}

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "for",
    "from",
    "in",
    "into",
    "is",
    "of",
    "on",
    "the",
    "to",
    "with",
}

WEAK_TITLE_TERMS = {
    "analysis",
    "hands-on",
    "live",
    "opinion",
    "podcast",
    "review",
    "sponsored",
    "video",
}

ACTION_KEYWORDS = {
    "launch",
    "launches",
    "launched",
    "release",
    "releases",
    "released",
    "announce",
    "announces",
    "announced",
    "introduce",
    "introduces",
    "introduced",
    "open-source",
    "open sources",
    "acquire",
    "acquires",
    "acquired",
    "raise",
    "raises",
    "raised",
    "debuts",
    "debut",
    "ship",
    "ships",
    "shipped",
    "upgrade",
    "upgrades",
    "updated",
    "update",
}

IMPORTANT_KEYWORDS = {
    "openai",
    "anthropic",
    "google",
    "deepmind",
    "github",
    "aws",
    "cloudflare",
    "kubernetes",
    "ai",
    "model",
    "api",
    "sdk",
    "security",
}

EXCLUDED_SUBSTRINGS = {
    "/podcasts/",
    "/podcast/",
    "/video/",
    "/videos/",
    "/events/",
    "/webinar/",
}

NOISY_TITLE_KEYWORDS = {
    "best deals",
    "big spring sale",
    "shopping",
    "buy now",
    "review roundup",
    "gift guide",
    "best apps",
    "wish you had more free time",
    "sale",
    "deals",
}

WEAK_NEWS_KEYWORDS = {
    "doge",
    "legal defeat",
    "lawsuit",
    "texted",
    "ad when i can",
    "celebrity",
    "cagefight",
    "spring sale",
}
