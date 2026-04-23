"""Entry point: fetch → summarize → email."""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import fetch_articles
from src.summarizer import summarize
from src.emailer import send_email
from config import OPENAI_API_KEY, SENDER_EMAIL, GMAIL_APP_PASSWORD

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def _validate_env():
    missing = []
    if not OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not SENDER_EMAIL:
        missing.append("GMAIL_SENDER")
    if not GMAIL_APP_PASSWORD:
        missing.append("GMAIL_APP_PASSWORD")
    if missing:
        log.error("Missing environment variables: %s", ", ".join(missing))
        sys.exit(1)


def run():
    log.info("=== Weekly News Agent Starting ===")
    _validate_env()

    log.info("Step 1/3 — Fetching articles from RSS feeds…")
    articles = fetch_articles()

    if not articles:
        log.warning("No relevant articles found. Sending empty digest.")

    log.info("Step 2/3 — Summarizing with OpenAI (%d articles)…", len(articles))
    digest = summarize(articles)

    log.info("Step 3/3 — Sending email…")
    send_email(digest)

    log.info("=== Done ===")


if __name__ == "__main__":
    run()
