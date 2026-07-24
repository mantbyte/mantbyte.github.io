"""
RSS Feed Reader — fetches and parses RSS feeds from configured sources.
Returns normalized article entries with title, link, summary, and date.
"""

import feedparser
from datetime import datetime, timedelta, timezone
from dateutil import parser as dateutil_parser


def fetch_feeds(feed_configs: list, max_age_hours: int = 48) -> list:
    """
    Fetch articles from multiple RSS feeds.
    
    Args:
        feed_configs: List of {"name": ..., "url": ..., "category": ...}
        max_age_hours: Only return articles published within this window
    
    Returns:
        List of normalized article dicts sorted by date (newest first)
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
    all_articles = []

    for feed_config in feed_configs:
        try:
            articles = _parse_single_feed(feed_config, cutoff)
            all_articles.extend(articles)
        except Exception as e:
            print(f"  ⚠️ Failed to parse {feed_config['name']}: {e}")
            continue

    # Sort by date, newest first
    all_articles.sort(key=lambda a: a["published"], reverse=True)

    # Deduplicate by title similarity
    all_articles = _deduplicate(all_articles)

    print(f"  📰 Collected {len(all_articles)} articles from {len(feed_configs)} feeds")
    return all_articles


def _parse_single_feed(feed_config: dict, cutoff: datetime) -> list:
    """Parse a single RSS feed and return normalized articles."""
    feed = feedparser.parse(feed_config["url"])
    articles = []

    for entry in feed.entries[:20]:  # Limit per feed to avoid overwhelming
        try:
            # Parse date
            published = _parse_date(entry)
            if published and published < cutoff:
                continue  # Too old

            # Extract summary
            summary = ""
            if hasattr(entry, "summary"):
                summary = _strip_html(entry.summary)[:500]
            elif hasattr(entry, "description"):
                summary = _strip_html(entry.description)[:500]

            articles.append({
                "title": entry.get("title", "Untitled"),
                "link": entry.get("link", ""),
                "summary": summary,
                "published": published or datetime.now(timezone.utc),
                "source": feed_config["name"],
                "category": feed_config["category"],
            })
        except Exception:
            continue

    return articles


def _parse_date(entry) -> datetime:
    """Try multiple date fields to extract a published date."""
    for field in ["published", "updated", "created"]:
        raw = entry.get(field) or entry.get(f"{field}_parsed")
        if raw:
            try:
                if isinstance(raw, str):
                    dt = dateutil_parser.parse(raw)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt
            except Exception:
                continue
    return None


def _strip_html(text: str) -> str:
    """Remove HTML tags from a string (simple approach)."""
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _deduplicate(articles: list) -> list:
    """Remove articles with very similar titles."""
    seen_titles = set()
    unique = []

    for article in articles:
        # Normalize: lowercase, strip common prefixes
        normalized = article["title"].lower().strip()
        # Use first 60 chars as a fingerprint
        fingerprint = normalized[:60]

        if fingerprint not in seen_titles:
            seen_titles.add(fingerprint)
            unique.append(article)

    return unique
