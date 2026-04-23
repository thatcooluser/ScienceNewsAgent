"""Fetches articles from RSS feeds, filters by topic, and deduplicates."""

import logging
from datetime import datetime, timezone, timedelta

import feedparser
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RSS_FEEDS, TOPICS, MAX_ARTICLES_PER_SOURCE, LOOKBACK_DAYS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

CUTOFF = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)


def _is_relevant(title: str, summary: str) -> bool:
    text = (title + " " + summary).lower()
    return any(topic.lower() in text for topic in TOPICS)


def _parse_date(entry) -> datetime:
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _title_key(title: str) -> frozenset:
    """Reduce a title to its significant words for duplicate detection."""
    stopwords = {"a","an","the","of","in","to","and","for","is","are","with","on","at","by"}
    words = title.lower().split()
    return frozenset(w for w in words if w not in stopwords and len(w) > 3)


def _deduplicate(articles: list[dict]) -> list[dict]:
    """
    Merge articles that cover the same story across sources.
    The first (most detailed) article is kept; others are listed under 'also_covered_by'.
    Two articles are considered duplicates when their title key overlaps by 40%+.
    """
    groups: list[dict] = []
    for article in articles:
        key = _title_key(article["title"])
        matched = False
        for group in groups:
            group_key = _title_key(group["title"])
            if not key or not group_key:
                continue
            overlap = len(key & group_key) / min(len(key), len(group_key))
            if overlap >= 0.4:
                group.setdefault("also_covered_by", []).append(article["source"])
                matched = True
                break
        if not matched:
            groups.append(dict(article))
    removed = len(articles) - len(groups)
    if removed:
        log.info("Deduplication removed %d redundant articles", removed)
    return groups


def fetch_articles() -> list[dict]:
    """
    Pull articles from all RSS feeds using only RSS summaries (no full-page scraping)
    to minimise OpenAI token usage. Deduplicates cross-source coverage before returning.
    """
    all_articles = []

    for source_name, feed_config in RSS_FEEDS.items():
        feed_url = feed_config["url"]
        topic_specific = feed_config["topic_specific"]

        log.info("Fetching: %s", source_name)
        try:
            feed = feedparser.parse(feed_url)
        except Exception as exc:
            log.warning("Failed to parse %s: %s", source_name, exc)
            continue

        if not feed.entries:
            log.warning("  No entries returned from %s", source_name)
            continue

        count = 0
        for entry in feed.entries:
            if count >= MAX_ARTICLES_PER_SOURCE:
                break

            pub_date = _parse_date(entry)
            if pub_date.year > 1970 and pub_date < CUTOFF:
                continue

            title = entry.get("title", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            link = entry.get("link", "")

            # Use RSS summary only — no full-page scraping (saves ~60% tokens)
            summary_text = BeautifulSoup(summary, "html.parser").get_text(" ", strip=True)[:600]

            if not topic_specific and not _is_relevant(title, summary_text):
                continue

            all_articles.append({
                "source": source_name,
                "title": title,
                "url": link,
                "published": pub_date.strftime("%Y-%m-%d") if pub_date.year > 1970 else "recent",
                "summary": summary_text,
                "also_covered_by": [],
            })
            count += 1

        log.info("  → %d articles from %s", count, source_name)

    log.info("Collected %d articles before deduplication", len(all_articles))
    return _deduplicate(all_articles)
