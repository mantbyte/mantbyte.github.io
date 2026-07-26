"""
Channel: Website Notification Center

Writes published articles directly to the 'notifications' Firestore collection,
which populates the notification bell on the Mantbyte website.
This is the primary notification channel and uses 100% free Firestore reads.
"""

from datetime import datetime

from distribution.channels.base import ChannelInterface, DistributionResult
from distribution.channels.push_channel import get_firestore_db


class WebsiteChannel(ChannelInterface):
    """
    Creates an in-app website notification for the new article.
    """

    COLLECTION = "site_notifications"

    def __init__(self, config: dict):
        self.config = config

    @property
    def name(self) -> str:
        return "website"

    def is_enabled(self, config: dict) -> bool:
        return config.get("enable_website_notifications", True)

    def distribute(self, article_event: dict) -> DistributionResult:
        """
        Create a new notification document in Firestore.
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

            notification = {
                "title": article_event.get("title", ""),
                "summary": article_event.get("excerpt", ""),
                "url": article_url,
                "featured_image": cover_image,
                "category": article_event.get("category", "Tech"),
                "published_at": article_event.get("published_at", datetime.utcnow().isoformat()),
                "read_count": 0,
                "priority": "normal",
                "slug": article_event.get("slug", ""),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Check for duplicate (same slug already notified)
            existing = (
                db.collection(self.COLLECTION)
                .where("slug", "==", notification["slug"])
                .limit(1)
                .get()
            )

            if len(list(existing)) > 0:
                print(f"  ℹ️ Website notification for '{notification['title'][:40]}...' already exists.")
                return DistributionResult(
                    channel=self.name,
                    status="skipped",
                    details={"reason": "Already exists"},
                )

            if self.config.get("dry_run"):
                print(f"  🧪 DRY RUN: Would have created website notification: {notification['title'][:50]}...")
                return DistributionResult(
                    channel=self.name,
                    status="success",
                    sent_count=1,
                    details={"dry_run": True, "notification_title": notification["title"]},
                )

            db.collection(self.COLLECTION).add(notification)
            print(f"  🔔 Website Notification created: {notification['title'][:50]}...")

            return DistributionResult(
                channel=self.name,
                status="success",
                sent_count=1,
                details={"notification_title": notification["title"]},
            )

        except Exception as e:
            print(f"  ❌ Failed to create website notification: {e}")
            return DistributionResult(
                channel=self.name,
                status="failed",
                error=str(e),
            )
