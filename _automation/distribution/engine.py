"""
Mantbyte Distribution Engine — Main Orchestrator

This is the entry point for the Distribution Engine.
It reads the article event, dispatches to all enabled channels,
records notification history, and updates analytics.

Usage:
    python _automation/distribution/engine.py [--test] [--digest]

Modes:
    Default:  Process a distribution_event.json file
    --test:   Run with a mock event for testing
    --digest: Send the daily digest (called by cron)
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add _automation to path
AUTOMATION_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(AUTOMATION_DIR)
sys.path.insert(0, AUTOMATION_DIR)

from distribution.config import load_config
from distribution.analytics import AnalyticsTracker
from distribution.channels.base import ChannelInterface, DistributionResult


def _discover_channels(config: dict) -> list:
    """
    Auto-discover and instantiate all enabled channels.

    Each channel module in channels/ is imported and checked
    for ChannelInterface subclasses. Only enabled channels are returned.
    """
    channels = []

    # Import all channel implementations
    from distribution.channels.rss_validator import RSSValidatorChannel
    from distribution.channels.website_channel import WebsiteChannel
    from distribution.channels.push_channel import PushChannel
    from distribution.channels.newsletter_channel import NewsletterChannel
    from distribution.channels.digest_channel import DigestChannel

    # Instantiate and filter by enabled, IN EXACT REQUESTED ORDER:
    # 1. RSS
    # 2. Website Notification
    # 3. Push
    # 4. Newsletter
    # 5. Digest (not used for event-based publishing but discovered)
    all_channels = [
        RSSValidatorChannel(config),
        WebsiteChannel(config),
        PushChannel(config),
        NewsletterChannel(config),
        DigestChannel(config),
    ]

    for channel in all_channels:
        if channel.is_enabled(config):
            channels.append(channel)
            print(f"  ✅ Channel enabled: {channel.name}")
        else:
            print(f"  ⏭️ Channel disabled: {channel.name}")

    return channels


def _load_event(event_path: str) -> dict:
    """Load and validate the distribution event file."""
    if not os.path.exists(event_path):
        print(f"  ❌ Event file not found: {event_path}")
        return {}

    with open(event_path, "r") as f:
        event = json.load(f)

    if event.get("event") != "article_published":
        print(f"  ⚠️ Unknown event type: {event.get('event')}")
        return {}

    required_fields = ["title", "slug", "url"]
    for field in required_fields:
        if not event.get(field):
            print(f"  ❌ Event missing required field: {field}")
            return {}

    return event


def _check_duplicate(db, slug: str, channel: str) -> bool:
    """
    Check notification_history to prevent duplicate notifications.

    Returns True if this article+channel combo was already sent.
    """
    if not db:
        return False

    try:
        existing = (
            db.collection("notification_history")
            .where("article_id", "==", slug)
            .where("channel", "==", channel)
            .where("status", "in", ["success", "partial"])
            .limit(1)
            .get()
        )
        return len(list(existing)) > 0
    except Exception:
        return False


def _record_history(db, slug: str, result: DistributionResult):
    """Record distribution result in notification_history."""
    if not db:
        return

    try:
        db.collection("notification_history").add({
            "article_id": slug,
            "channel": result.channel,
            "status": result.status,
            "sent_at": datetime.utcnow().isoformat(),
            "delivery_count": result.sent_count,
            "failed_count": result.failed_count,
            "error": result.error,
            "details": result.details,
        })
    except Exception as e:
        print(f"  ⚠️ Failed to record history for {result.channel}: {e}")


def run_distribution(event_path: str = None):
    """
    Main distribution flow.

    1. Load config
    2. Load event
    3. Discover channels
    4. Dispatch to each channel (with duplicate prevention)
    5. Record history + analytics
    """
    print("\n" + "=" * 60)
    print("📡 MANTBYTE DISTRIBUTION ENGINE v1")
    print("=" * 60)

    # 1. Load config
    config = load_config()
    print("  ✅ Configuration loaded.\n")

    # 2. Load event
    if event_path is None:
        event_path = os.path.join(AUTOMATION_DIR, "distribution_event.json")

    event = _load_event(event_path)
    if not event:
        print("  ❌ No valid distribution event. Exiting.")
        return False

    slug = event.get("slug", "")
    print(f"  📄 Article: {event.get('title', 'Unknown')[:60]}")
    print(f"  🏷️ Category: {event.get('category', 'Unknown')}")
    print(f"  🔗 URL: {event.get('url', 'Unknown')}")
    print()

    # 3. Get Firestore (optional)
    db = None
    try:
        from distribution.channels.push_channel import get_firestore_db
        db = get_firestore_db(config)
    except Exception:
        print("  ⚠️ Firestore not available. History/analytics disabled.\n")

    # 4. Init analytics
    analytics = AnalyticsTracker(db)
    analytics.record_article_published()

    # 5. Discover and run channels
    channels = _discover_channels(config)
    print()

    results = []
    for channel in channels:
        print(f"  {'─' * 40}")
        print(f"  📡 Channel: {channel.name}")

        # Duplicate check
        if _check_duplicate(db, slug, channel.name):
            print(f"  ⏭️ Already notified for this article. Skipping.")
            results.append(DistributionResult(
                channel=channel.name,
                status="skipped",
                details={"reason": "Duplicate prevention"},
            ))
            continue

        try:
            result = channel.distribute(event)
            results.append(result)
            _record_history(db, slug, result)

            # Update analytics
            if channel.name == "push" and result.is_success:
                analytics.record_push_sent(result.sent_count)
                if result.failed_count > 0:
                    analytics.record_push_failed(result.failed_count)
            elif channel.name == "digest" and result.is_success:
                analytics.record_digest_generated()

        except Exception as e:
            print(f"  ❌ Channel {channel.name} failed: {e}")
            result = DistributionResult(
                channel=channel.name,
                status="failed",
                error=str(e),
            )
            results.append(result)
            _record_history(db, slug, result)

    # 6. Print summary
    _print_summary(results)
    return True


def run_digest():
    """
    Send the daily digest.
    Called by the daily-digest GitHub Action cron.
    """
    print("\n" + "=" * 60)
    print("📬 MANTBYTE DAILY DIGEST")
    print("=" * 60)

    config = load_config()
    print("  ✅ Configuration loaded.\n")

    from distribution.channels.digest_channel import DigestChannel

    digest = DigestChannel(config)

    if not digest.is_enabled(config):
        print("  ⏭️ Digest channel is disabled. Exiting.")
        return True

    result = digest.send_digest()

    print(f"\n  {'─' * 40}")
    print(f"  Status: {result.status}")
    print(f"  Sent: {result.sent_count}")
    print(f"  Failed: {result.failed_count}")
    if result.error:
        print(f"  Error: {result.error}")
    print(f"  {'─' * 40}\n")

    return result.is_success


def run_test():
    """Run with a mock event for testing."""
    print("  🧪 Running in TEST mode with mock event.\n")

    mock_event = {
        "event": "article_published",
        "title": "Understanding AI-Generated CORS Vulnerabilities",
        "slug": "ai-generated-cors-vulnerabilities-test",
        "category": "Tech",
        "excerpt": "A deep dive into how AI code assistants can inadvertently introduce CORS misconfigurations.",
        "url": "/tech/2026/07/25/ai-generated-cors-vulnerabilities-test.html",
        "cover_image": "/assets/images/posts/default-cover.png",
        "tags": ["AI", "Security", "CORS"],
        "published_at": datetime.utcnow().isoformat(),
        "filename": "2026-07-25-ai-generated-cors-vulnerabilities-test.md",
    }

    # Write mock event
    event_path = os.path.join(AUTOMATION_DIR, "distribution_event_test.json")
    with open(event_path, "w") as f:
        json.dump(mock_event, f, indent=2)

    run_distribution(event_path)

    # Clean up
    if os.path.exists(event_path):
        os.remove(event_path)


def _print_summary(results: list):
    """Print end-of-run summary."""
    print(f"\n{'=' * 60}")
    print("📊 DISTRIBUTION SUMMARY")
    print("=" * 60)

    for r in results:
        emoji = {"success": "✅", "partial": "⚠️", "failed": "❌", "skipped": "⏭️"}.get(r.status, "❓")
        line = f"  {emoji} {r.channel:15s} → {r.status}"
        if r.sent_count > 0:
            line += f" ({r.sent_count} sent)"
        if r.failed_count > 0:
            line += f" ({r.failed_count} failed)"
        if r.error:
            line += f" — {r.error[:50]}"
        print(line)

    print("=" * 60 + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mantbyte Distribution Engine")
    parser.add_argument("--test", action="store_true", help="Run with mock event")
    parser.add_argument("--digest", action="store_true", help="Send daily digest")
    parser.add_argument("--event", type=str, help="Path to event JSON file")
    args = parser.parse_args()

    if args.test:
        run_test()
    elif args.digest:
        success = run_digest()
        sys.exit(0 if success else 1)
    else:
        success = run_distribution(args.event)
        sys.exit(0 if success else 1)
