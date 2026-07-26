"""
Distribution Engine — Analytics Tracker

Tracks distribution metrics in Firestore using atomic increments.
Collection: distribution_metrics/global
"""

from datetime import datetime


class AnalyticsTracker:
    """
    Tracks distribution metrics in Firestore.

    All operations use atomic increments to avoid race conditions.
    Falls back gracefully if Firestore is unavailable.
    """

    COLLECTION = "distribution_metrics"
    DOCUMENT = "global"

    def __init__(self, firestore_db):
        """
        Args:
            firestore_db: Firebase Admin Firestore client instance.
                         Can be None if Firebase is not configured.
        """
        self.db = firestore_db

    def _increment(self, field: str, value: int = 1):
        """Atomically increment a metric field."""
        if not self.db:
            return
        try:
            from google.cloud.firestore_v1 import Increment
            doc_ref = self.db.collection(self.COLLECTION).document(self.DOCUMENT)
            doc_ref.set(
                {
                    field: Increment(value),
                    "last_distribution_at": datetime.utcnow().isoformat(),
                },
                merge=True,
            )
        except Exception as e:
            print(f"  ⚠️ Analytics update failed for {field}: {e}")

    def record_article_published(self):
        """Increment articles_published counter."""
        self._increment("articles_published")

    def record_push_sent(self, count: int = 1):
        """Record successful push notifications."""
        self._increment("push_sent", count)

    def record_push_failed(self, count: int = 1):
        """Record failed push notifications."""
        self._increment("push_failed", count)

    def record_digest_generated(self):
        """Record a daily digest generation."""
        self._increment("digest_generated")

    def record_subscriber_added(self):
        """Record new newsletter subscriber."""
        self._increment("newsletter_subscribers")

    def record_subscriber_verified(self):
        """Record a subscriber verification."""
        self._increment("verified_subscribers")

    def get_metrics(self) -> dict:
        """
        Fetch current metrics snapshot.

        Returns:
            Dict of all metrics, or empty dict if unavailable.
        """
        if not self.db:
            return {}
        try:
            doc = self.db.collection(self.COLLECTION).document(self.DOCUMENT).get()
            return doc.to_dict() if doc.exists else {}
        except Exception as e:
            print(f"  ⚠️ Failed to fetch analytics: {e}")
            return {}
