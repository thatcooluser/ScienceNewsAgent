"""Run this to diagnose why scraper returns no articles."""
import feedparser
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from config import RSS_FEEDS, TOPICS, LOOKBACK_DAYS

CUTOFF = datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)

for source, cfg in RSS_FEEDS.items():
    url = cfg["url"]
    print(f"\n{'='*60}")
    print(f"SOURCE: {source}")
    feed = feedparser.parse(url)
    entries = feed.entries
    print(f"  Total entries in feed: {len(entries)}")

    if not entries:
        print("  WARNING: Feed returned 0 entries — URL may be broken")
        continue

    # Show first entry date to check cutoff issue
    first = entries[0]
    pub = getattr(first, "published_parsed", None) or getattr(first, "updated_parsed", None)
    if pub:
        pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
        print(f"  Most recent article date: {pub_dt.date()}  (cutoff: {CUTOFF.date()})")
        if pub_dt < CUTOFF:
            print("  !! All articles older than cutoff — try increasing LOOKBACK_DAYS in config.py")
    else:
        print("  WARNING: No date found on entries — date filtering will drop all articles")

    # Check keyword matching
    matched = 0
    for e in entries[:10]:
        title = e.get("title", "")
        summary = BeautifulSoup(e.get("summary", ""), "html.parser").get_text()
        text = (title + " " + summary).lower()
        if any(t.lower() in text for t in TOPICS):
            matched += 1
            print(f"  MATCH: {title[:80]}")

    if matched == 0:
        print("  !! No keyword matches in first 10 entries")
        print(f"  Sample titles:")
        for e in entries[:3]:
            print(f"    - {e.get('title','?')[:80]}")
