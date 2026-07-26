"""
Channel: Newsletter Queue

When a new article is published, this channel queues it into
the Firestore daily_digest_queue for later batch delivery.

This channel does NOT send email directly.
The digest_channel handles actual email delivery on a schedule.
"""

from datetime import datetime

from distribution.channels.base import ChannelInterface, DistributionResult
from distribution.channels.push_channel import get_firestore_db


class NewsletterChannel(ChannelInterface):
    """
    Queues published articles for newsletter delivery.

    Architecture:
        Article Published → Queue in Firestore → Daily Digest sends batch email

    This separation allows:
        - Multiple articles queued before a single digest
        - Configurable digest schedule
        - No email sent per-article (reduces spam risk)
    """

    QUEUE_COLLECTION = "daily_digest_queue"

    def __init__(self, config: dict):
        self.config = config

    @property
    def name(self) -> str:
        return "newsletter"

    def is_enabled(self, config: dict) -> bool:
        return config.get("enable_newsletter", False)

    def distribute(self, article_event: dict) -> DistributionResult:
        """
        Queue the article into the daily digest queue.

        Does NOT send email. That's the digest_channel's job.
        """
        db = get_firestore_db(self.config)
        if not db:
            return DistributionResult(
                channel=self.name,
                status="skipped",
                details={"reason": "Firebase not configured"},
            )

        try:
            site_url = self.config.get("site_url", "https://mantbyte.github.io")
            article_url = article_event.get("url", "")
            if article_url and not article_url.startswith("http"):
                article_url = f"{site_url.rstrip('/')}{article_url}"

            cover_image = article_event.get("cover_image", "")
            if cover_image and not cover_image.startswith("http"):
                cover_image = f"{site_url.rstrip('/')}{cover_image}"

            queue_entry = {
                "title": article_event.get("title", ""),
                "summary": article_event.get("excerpt", ""),
                "url": article_url,
                "category": article_event.get("category", "Tech"),
                "published_at": article_event.get("published_at", datetime.utcnow().isoformat()),
                "featured_image": cover_image,
                "slug": article_event.get("slug", ""),
                "queued_at": datetime.utcnow().isoformat(),
                "delivered": False,
            }

            # Check for duplicate (same slug already queued)
            existing = (
                db.collection(self.QUEUE_COLLECTION)
                .where("slug", "==", queue_entry["slug"])
                .where("delivered", "==", False)
                .limit(1)
                .get()
            )

            if len(list(existing)) > 0:
                print(f"  ℹ️ Article '{queue_entry['title'][:40]}...' already in digest queue.")
                return DistributionResult(
                    channel=self.name,
                    status="skipped",
                    details={"reason": "Already queued"},
                )

            if self.config.get("dry_run"):
                print(f"  🧪 DRY RUN: Would have queued for daily digest: {queue_entry['title'][:50]}...")
                return DistributionResult(
                    channel=self.name,
                    status="success",
                    sent_count=1,
                    details={"dry_run": True, "queued_title": queue_entry["title"]},
                )

            db.collection(self.QUEUE_COLLECTION).add(queue_entry)
            print(f"  📬 Queued for daily digest: {queue_entry['title'][:50]}...")

            return DistributionResult(
                channel=self.name,
                status="success",
                sent_count=1,
                details={"queued_title": queue_entry["title"]},
            )

        except Exception as e:
            print(f"  ❌ Failed to queue article: {e}")
            return DistributionResult(
                channel=self.name,
                status="failed",
                error=str(e),
            )
