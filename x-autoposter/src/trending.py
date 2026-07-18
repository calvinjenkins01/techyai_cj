"""Find trending AI topics from RSS/Atom feeds of major tech publications.

Uses only the standard library (urllib + ElementTree) so there are no fragile
feed-parsing dependencies.
"""

import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from email.utils import parsedate_to_datetime

FEEDS = [
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "https://venturebeat.com/category/ai/feed/",
    "https://arstechnica.com/ai/feed/",
]

# Topics mentioning these score higher — matches the account's niche:
# AI news, Claude/Anthropic, ChatGPT/OpenAI, and building things with AI.
BOOST_KEYWORDS = [
    "claude", "anthropic", "chatgpt", "openai", "gemini", "ai agent", "llm",
    "copilot", "cursor", "vibe coding", "coding assistant", "build", "developer",
    "app", "automation", "no-code",
]

MAX_AGE_HOURS = 72
ATOM = "{http://www.w3.org/2005/Atom}"


@dataclass
class Topic:
    title: str
    link: str
    summary: str
    published: float
    score: float


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


def _parse_date(value: str) -> float | None:
    if not value:
        return None
    try:  # RFC 822 (RSS)
        return parsedate_to_datetime(value).timestamp()
    except (ValueError, TypeError):
        pass
    try:  # ISO 8601 (Atom)
        from datetime import datetime

        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _parse_feed(xml_data: bytes) -> list[dict]:
    root = ET.fromstring(xml_data)
    entries = []
    # RSS 2.0
    for item in root.iter("item"):
        entries.append({
            "title": item.findtext("title", ""),
            "link": item.findtext("link", ""),
            "summary": _strip_html(item.findtext("description", "")),
            "date": _parse_date(item.findtext("pubDate", "")),
        })
    # Atom
    for entry in root.iter(f"{ATOM}entry"):
        link_el = entry.find(f"{ATOM}link")
        entries.append({
            "title": entry.findtext(f"{ATOM}title", ""),
            "link": link_el.get("href", "") if link_el is not None else "",
            "summary": _strip_html(
                entry.findtext(f"{ATOM}summary", "") or entry.findtext(f"{ATOM}content", "")
            ),
            "date": _parse_date(entry.findtext(f"{ATOM}updated", "")),
        })
    return entries


def fetch_trending(exclude_links: set[str]) -> list[Topic]:
    """Return candidate topics from all feeds, newest and most relevant first."""
    now = time.time()
    topics = []
    for url in FEEDS:
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(request, timeout=30) as resp:
                entries = _parse_feed(resp.read())
        except Exception as exc:  # a dead feed shouldn't kill the run
            print(f"Warning: could not fetch {url}: {exc}")
            continue
        for entry in entries[:15]:
            link = entry["link"]
            if not link or link in exclude_links:
                continue
            ts = entry["date"] or now
            age_hours = (now - ts) / 3600
            if age_hours > MAX_AGE_HOURS:
                continue
            text = f"{entry['title']} {entry['summary']}".lower()
            keyword_hits = sum(1 for kw in BOOST_KEYWORDS if kw in text)
            # Fresher articles and niche-relevant keywords rank higher.
            score = keyword_hits * 10 + max(0.0, MAX_AGE_HOURS - age_hours) / 10
            topics.append(Topic(entry["title"], link, entry["summary"][:1000], ts, score))
    topics.sort(key=lambda t: t.score, reverse=True)
    return topics
