"""AI-news autoposter for X.

Finds a trending AI topic, writes a long-form article with Claude, renders a
header image, and posts to X. Designed to run every other day via GitHub Actions.

Usage:
    python main.py            # dry run: writes the article + image to drafts/
    python main.py --post     # actually publish to X
    python main.py --post --force   # publish even on an "off" day
"""

import argparse
import json
import sys
import time
from pathlib import Path

from src.generate import generate_article
from src.image import render_card
from src.trending import fetch_trending

ROOT = Path(__file__).parent
STATE_FILE = ROOT / "state.json"
DRAFTS_DIR = ROOT / "drafts"

# X allows 25,000 chars with Premium. Keep articles shorter — long enough to be
# an article, short enough that people actually read it.
MAX_POST_CHARS = 4000


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"posted_links": [], "last_posted_day": None}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def is_posting_day(state: dict) -> bool:
    """Every-other-day gate: post when at least 2 days passed since the last post."""
    today = int(time.time() // 86400)
    last = state.get("last_posted_day")
    return last is None or today - last >= 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--post", action="store_true", help="publish to X (default: dry run)")
    parser.add_argument("--force", action="store_true", help="ignore the every-other-day gate")
    args = parser.parse_args()

    state = load_state()
    if args.post and not args.force and not is_posting_day(state):
        print("Not a posting day (posted less than 2 days ago). Exiting.")
        return 0

    print("Fetching trending topics...")
    topics = fetch_trending(exclude_links=set(state["posted_links"]))
    if not topics:
        print("No fresh topics found. Exiting.")
        return 0
    topic = topics[0]
    print(f"Selected topic: {topic.title}")

    print("Generating article with Claude...")
    article = generate_article(topic, MAX_POST_CHARS)

    DRAFTS_DIR.mkdir(exist_ok=True)
    stamp = time.strftime("%Y-%m-%d")
    image_path = str(DRAFTS_DIR / f"{stamp}-header.png")
    render_card(article["headline"], article["subheadline"], image_path)
    draft_path = DRAFTS_DIR / f"{stamp}-article.txt"
    draft_path.write_text(article["post_text"] + "\n")
    print(f"Draft written: {draft_path} ({len(article['post_text'])} chars)")
    print(f"Header image: {image_path}")

    if not args.post:
        print("Dry run complete. Re-run with --post to publish.")
        return 0

    from src.post import post_to_x

    url = post_to_x(article["post_text"], image_path)
    print(f"Posted: {url}")

    state["posted_links"] = (state["posted_links"] + [topic.link])[-100:]
    state["last_posted_day"] = int(time.time() // 86400)
    save_state(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
