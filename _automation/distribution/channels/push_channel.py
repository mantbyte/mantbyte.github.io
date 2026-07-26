"""
Channel: Push Notifications via Firebase Cloud Messaging (FCM)

Sends browser push notifications to all active subscribers
when a new article is published.

Requires:
    - Firebase Admin SDK (firebase-admin)
    - FIREBASE_SERVICE_ACCOUNT env var (JSON string)
    - Firestore collection: notification_subscribers
"""

import json
import os
from typing import Optional

from distribution.channels.base import ChannelInterface, DistributionResult


# Firebase Admin SDK is imported lazily to avoid breaking
# when not installed (e.g., during dry runs)
_firebase_initialized = False
_firestore_db = None


def _init_firebase(service_account_json: str):
    """
    Initialize Firebase Admin SDK (singleton).

    Args:
        service_account_json: JSON string of the service account credentials.
    """
    global _firebase_initialized, _firestore_db

    if _firebase_initialized:
        return _firestore_db

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not service_account_json:
            print("  ⚠️ FIREBASE_SERVICE_ACCOUNT not set. Push notifications disabled.")
            return None

        # Parse the JSON string
        try:
            cred_dict = json.loads(service_account_json)
        except json.JSONDecodeError:
            # Maybe it's a file path
            if os.path.exists(service_account_json):
                cred_dict = json.load(open(service_account_json))
            else:
                print("  ❌ Invalid FIREBASE_SERVICE_ACCOUNT format.")
                return None

        # Check if already initialized
        try:
            app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate(cred_dict)
            app = firebase_admin.initialize_app(cred)

        _firestore_db = firestore.client()
        _firebase_initialized = True
        print("  🔥 Firebase Admin SDK initialized.")
        return _firestore_db

    except ImportError:
        print("  ⚠️ firebase-admin not installed. Push notifications disabled.")
        return None
    except Exception as e:
        print(f"  ❌ Firebase init failed: {e}")
        return None


def get_firestore_db(config: dict):
    """Get or initialize the Firestore database client."""
    global _firestore_db
    if _firestore_db:
        return _firestore_db
    sa = config.get("firebase_service_account", "")
    return _init_firebase(sa)


class PushChannel(ChannelInterface):
    """
    Send push notifications via Firebase Cloud Messaging.

    Architecture:
        1. Query Firestore for all active notification tokens
        2. Build notification payload with article metadata
        3. Send via FCM send_each() for batch efficiency
        4. Auto-clean invalid/expired tokens
    """

    COLLECTION = "notification_tokens"

    def __init__(self, config: dict):
        self.config = config
        self.push_config = config.get("push_notification", {})
        self.max_per_run = config.get("max_notifications_per_run", 500)

    @property
    def name(self) -> str:
        return "push"

    def is_enabled(self, config: dict) -> bool:
        return config.get("enable_push", False)

    def distribute(self, article_event: dict) -> DistributionResult:
        """Send push notifications to all active FCM subscribers."""
        db = get_firestore_db(self.config)
        if not db:
            return DistributionResult(
                channel=self.name,
                status="skipped",
                details={"reason": "Firebase not configured"},
            )

        try:
            from firebase_admin import messaging
        except ImportError:
            return DistributionResult(
                channel=self.name,
                status="skipped",
                details={"reason": "firebase-admin not installed"},
            )

        # 1. Fetch active tokens
        print("  📱 Fetching active push tokens...")
        tokens = self._get_active_tokens(db)

        if not tokens:
            print("  ℹ️ No active push tokens found.")
            return DistributionResult(
                channel=self.name,
                status="success",
                sent_count=0,
                details={"reason": "No tokens"},
            )

        # Limit batch size
        tokens = tokens[: self.max_per_run]
        print(f"  📱 Sending push to {len(tokens)} devices...")

        # 2. Build notification
        site_url = self.config.get("site_url", "https://mantbyte.github.io")
        article_url = article_event.get("url", "")
        if article_url and not article_url.startswith("http"):
            article_url = f"{site_url.rstrip('/')}{article_url}"

        cover_image = article_event.get("cover_image", "")
        if cover_image and not cover_image.startswith("http"):
            cover_image = f"{site_url.rstrip('/')}{cover_image}"

        notification = messaging.Notification(
            title=self.push_config.get("title_prefix", "🚀 New Mantbyte Article"),
            body=article_event.get("title", "New article published"),
            image=cover_image if cover_image else None,
        )

        webpush_config = messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                icon=f"{site_url}{self.push_config.get('icon', '/assets/images/favicon.svg')}",
                badge=f"{site_url}{self.push_config.get('badge', '/assets/images/favicon.svg')}",
                tag=f"mantbyte-{article_event.get('slug', 'article')}",
                renotify=True,
            ),
            fcm_options=messaging.WebpushFCMOptions(
                link=article_url,
            ),
        )

        # 3. Send batch
        messages = [
            messaging.Message(
                notification=notification,
                webpush=webpush_config,
                token=token,
            )
            for token in tokens
        ]

        try:
            response = messaging.send_each(messages)
        except Exception as e:
            print(f"  ❌ FCM send_each failed: {e}")
            return DistributionResult(
                channel=self.name,
                status="failed",
                error=str(e),
                failed_count=len(tokens),
            )

        # 4. Process results & clean invalid tokens
        success_count = response.success_count
        failure_count = response.failure_count
        invalid_tokens = []

        for i, send_response in enumerate(response.responses):
            if send_response.exception:
                error_code = getattr(send_response.exception, "code", "")
                # Clean up tokens that are no longer valid
                if error_code in (
                    "NOT_FOUND",
                    "UNREGISTERED",
                    "INVALID_ARGUMENT",
                    "messaging/registration-token-not-registered",
                ):
                    invalid_tokens.append(tokens[i])

        # Deactivate invalid tokens
        if invalid_tokens:
            self._deactivate_tokens(db, invalid_tokens)
            print(f"  🧹 Deactivated {len(invalid_tokens)} invalid tokens.")

        status = "success" if failure_count == 0 else "partial"
        print(f"  ✅ Push: {success_count} sent, {failure_count} failed")

        return DistributionResult(
            channel=self.name,
            status=status,
            sent_count=success_count,
            failed_count=failure_count,
            details={
                "invalid_tokens_cleaned": len(invalid_tokens),
                "total_tokens": len(tokens),
            },
        )

    def _get_active_tokens(self, db) -> list:
        """Fetch all active FCM tokens from Firestore."""
        try:
            docs = (
                db.collection(self.COLLECTION)
                .where("active", "==", True)
                .limit(self.max_per_run)
                .get()
            )
            return [doc.to_dict().get("token") for doc in docs if doc.to_dict().get("token")]
        except Exception as e:
            print(f"  ❌ Failed to fetch tokens: {e}")
            return []

    def _deactivate_tokens(self, db, invalid_tokens: list):
        """Mark invalid tokens as inactive in Firestore."""
        try:
            collection = db.collection(self.COLLECTION)
            for token in invalid_tokens:
                docs = collection.where("token", "==", token).limit(1).get()
                for doc in docs:
                    doc.reference.update({"active": False})
        except Exception as e:
            print(f"  ⚠️ Failed to deactivate tokens: {e}")
