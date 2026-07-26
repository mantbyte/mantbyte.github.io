"""
Channel: Daily Digest

Sends a compiled daily digest email to all verified newsletter subscribers.
Runs on a separate GitHub Actions cron schedule (not per-article).

Flow:
    1. Read daily_digest_queue from Firestore (undelivered items)
    2. Generate HTML/text email digest
    3. Send to all verified, active subscribers
    4. Mark queue items as delivered
"""

from datetime import datetime
from typing import Optional

from distribution.channels.base import ChannelInterface, DistributionResult
from distribution.channels.push_channel import get_firestore_db


class DigestChannel(ChannelInterface):
    """
    Compiles and saves daily digest to Firestore.
    Emails via EmailProvider if configured.

    This channel is different from others: it's not triggered per-article,
    but on a schedule (via GitHub Actions cron). When triggered, it:
    1. Collects all undelivered articles from the queue
    2. Generates a digest html/text
    3. Saves it to Firestore
    4. Sends to all verified subscribers (if EmailProvider exists)
    """

    QUEUE_COLLECTION = "daily_digest_queue"
    SUBSCRIBERS_COLLECTION = "subscribers"

    def __init__(self, config: dict):
        self.config = config
        self.digest_config = config.get("digest", {})

    @property
    def name(self) -> str:
        return "digest"

    def is_enabled(self, config: dict) -> bool:
        return config.get("enable_digest", False)

    def distribute(self, article_event: dict) -> DistributionResult:
        """
        When called per-article, this is a no-op.
        The actual digest is sent via send_digest() on a schedule.
        """
        # Per-article: just return success (queuing is handled by newsletter_channel)
        return DistributionResult(
            channel=self.name,
            status="skipped",
            details={"reason": "Digest runs on schedule, not per-article"},
        )

    def send_digest(self) -> DistributionResult:
        """
        Compile and save the daily digest to Firestore.
        Send via EmailProvider ONLY if configured.
        """
        db = get_firestore_db(self.config)
        if not db:
            return DistributionResult(
                channel=self.name,
                status="skipped",
                details={"reason": "Firebase not configured"},
            )

        # 1. Fetch undelivered queue items
        print("  📰 Fetching digest queue...")
        articles = self._get_queued_articles(db)

        if not articles:
            print("  ℹ️ No articles in digest queue. Nothing to send.")
            return DistributionResult(
                channel=self.name,
                status="success",
                details={"reason": "Empty queue"},
            )

        print(f"  📰 {len(articles)} articles in digest queue.")

        # 2. Generate digest email content
        html_body = self._generate_html_digest(articles)
        text_body = self._generate_text_digest(articles)

        today = datetime.utcnow().strftime("%B %d, %Y")
        subject = f"{self.digest_config.get('subject_prefix', 'Mantbyte Daily Digest')} — {today}"

        # 3. Store Digest in Firestore (always)
        if self.config.get("dry_run"):
            print(f"  🧪 DRY RUN: Would have stored digest in Firestore.")
        else:
            try:
                db.collection("daily_digest").add({
                    "date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "subject": subject,
                    "html": html_body,
                    "plaintext": text_body,
                    "generated_at": datetime.utcnow().isoformat(),
                    "articles": [a.get("slug") for a in articles],
                    "status": "generated"
                })
                print(f"  💾 Digest stored in Firestore.")
            except Exception as e:
                print(f"  ⚠️ Failed to store digest in Firestore: {e}")

        # 4. Optional: Send via Email Provider
        email_provider = self.config.get("email_provider")
        if not email_provider or self.config.get("dry_run"):
            if self.config.get("dry_run"):
                print("  🧪 DRY RUN: Digest generated, but not emailed or marked as delivered.")
            else:
                print("  ⏭️ No EmailProvider configured. Digest saved, but not emailed.")
                # Still mark as delivered so they don't pile up
                self._mark_delivered(db, articles)
                
            return DistributionResult(
                channel=self.name,
                status="success",
                sent_count=0,
                details={"reason": "Generated, not emailed (no provider or dry run)"},
            )

        # 5. Fetch verified subscribers (if emailing)
        subscribers = self._get_verified_subscribers(db)

        if not subscribers:
            print("  ℹ️ No verified subscribers. Skipping email digest.")
            self._mark_delivered(db, articles)
            return DistributionResult(
                channel=self.name,
                status="success",
                details={"reason": "No verified subscribers"},
            )

        print(f"  📧 Sending digest via EmailProvider to {len(subscribers)} subscribers...")

        # 6. Send batch
        result = email_provider.send_digest(
            recipients=subscribers,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
            from_name=self.config.get("site_name", "Mantbyte"),
        )

        # 7. Mark queue items as delivered
        if result["sent"] > 0:
            self._mark_delivered(db, articles)
            print(f"  ✅ Digest sent: {result['sent']} delivered, {result['failed']} failed")
        else:
            print(f"  ❌ Digest delivery failed entirely.")

        return DistributionResult(
            channel=self.name,
            status="success" if result["failed"] == 0 else "partial",
            sent_count=result["sent"],
            failed_count=result["failed"],
            details={
                "articles_in_digest": len(articles),
                "subscribers": len(subscribers),
            },
        )

    def _get_queued_articles(self, db) -> list:
        """Fetch undelivered articles from the digest queue."""
        try:
            max_articles = self.digest_config.get("max_articles", 10)
            docs = (
                db.collection(self.QUEUE_COLLECTION)
                .where("delivered", "==", False)
                .order_by("queued_at")
                .limit(max_articles)
                .get()
            )
            articles = []
            for doc in docs:
                data = doc.to_dict()
                data["_doc_id"] = doc.id
                articles.append(data)
            return articles
        except Exception as e:
            print(f"  ❌ Failed to fetch digest queue: {e}")
            return []

    def _get_verified_subscribers(self, db) -> list:
        """Fetch all verified, active subscriber emails."""
        try:
            docs = (
                db.collection(self.SUBSCRIBERS_COLLECTION)
                .where("verified", "==", True)
                .where("is_active", "==", True)
                .get()
            )
            return [doc.to_dict().get("email") for doc in docs if doc.to_dict().get("email")]
        except Exception as e:
            print(f"  ❌ Failed to fetch subscribers: {e}")
            return []

    def _mark_delivered(self, db, articles: list):
        """Mark queued articles as delivered."""
        try:
            for article in articles:
                doc_id = article.get("_doc_id")
                if doc_id:
                    db.collection(self.QUEUE_COLLECTION).document(doc_id).update({
                        "delivered": True,
                        "delivered_at": datetime.utcnow().isoformat(),
                    })
        except Exception as e:
            print(f"  ⚠️ Failed to mark articles as delivered: {e}")

    def _generate_html_digest(self, articles: list) -> str:
        """Generate HTML email for the daily digest."""
        site_url = self.config.get("site_url", "https://mantbyte.github.io")
        today = datetime.utcnow().strftime("%B %d, %Y")

        articles_html = ""
        for article in articles:
            featured_image = article.get("featured_image", "")
            image_html = ""
            if featured_image:
                image_html = f'''
                    <img src="{featured_image}" alt="{article.get("title", "")}"
                         style="width: 100%; height: 180px; object-fit: cover; border-radius: 8px 8px 0 0;">'''

            articles_html += f'''
                <table role="presentation" style="width: 100%; margin-bottom: 24px; border: 1px solid #eaeaea; border-radius: 8px; overflow: hidden;">
                    <tr><td>{image_html}</td></tr>
                    <tr>
                        <td style="padding: 20px;">
                            <span style="display: inline-block; padding: 2px 10px; background: #f0f0f0; border-radius: 4px; font-size: 11px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">{article.get("category", "Tech")}</span>
                            <h3 style="margin: 8px 0; font-size: 18px; font-weight: 700; color: #111;">
                                <a href="{article.get("url", "#")}" style="color: #111; text-decoration: none;">{article.get("title", "")}</a>
                            </h3>
                            <p style="margin: 0; font-size: 14px; line-height: 1.5; color: #555;">{article.get("summary", "")[:200]}</p>
                            <a href="{article.get("url", "#")}" style="display: inline-block; margin-top: 12px; font-size: 13px; font-weight: 600; color: #111; text-decoration: none;">Read more →</a>
                        </td>
                    </tr>
                </table>'''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mantbyte Daily Digest — {today}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8f9fa; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="width: 580px; max-width: 100%; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 32px 40px; border-bottom: 1px solid #eaeaea;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; font-size: 22px; font-weight: 700; color: #111; letter-spacing: -0.5px;">mantbyte</h1>
                                    </td>
                                    <td style="text-align: right;">
                                        <span style="font-size: 13px; color: #999;">{today}</span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Intro -->
                    <tr>
                        <td style="padding: 32px 40px 16px;">
                            <h2 style="margin: 0 0 8px; font-size: 20px; font-weight: 700; color: #111;">Today's Articles</h2>
                            <p style="margin: 0; font-size: 14px; color: #666; line-height: 1.5;">
                                Here's what's new on Mantbyte today.
                            </p>
                        </td>
                    </tr>
                    <!-- Articles -->
                    <tr>
                        <td style="padding: 16px 40px 32px;">
                            {articles_html}
                        </td>
                    </tr>
                    <!-- CTA -->
                    <tr>
                        <td style="padding: 0 40px 32px; text-align: center;">
                            <a href="{site_url}" style="display: inline-block; padding: 14px 32px; background: #111; color: #fff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px;">Read all on Mantbyte →</a>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; background: #fafafa; border-top: 1px solid #eaeaea; text-align: center;">
                            <p style="margin: 0 0 8px; font-size: 12px; color: #999;">
                                You're receiving this because you subscribed to Mantbyte.
                            </p>
                            <p style="margin: 0; font-size: 12px;">
                                <a href="{site_url}/verify?action=unsubscribe" style="color: #999; text-decoration: underline;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    def _generate_text_digest(self, articles: list) -> str:
        """Generate plain text version of the daily digest."""
        site_url = self.config.get("site_url", "https://mantbyte.github.io")
        today = datetime.utcnow().strftime("%B %d, %Y")

        lines = [
            f"Mantbyte Daily Digest — {today}",
            "=" * 40,
            "",
            "Today's Articles",
            "",
        ]

        for article in articles:
            lines.append(f"• {article.get('title', '')}")
            lines.append(f"  {article.get('summary', '')[:150]}")
            lines.append(f"  Read: {article.get('url', '#')}")
            lines.append("")

        lines.extend([
            f"Read all → {site_url}",
            "",
            "---",
            "You're receiving this because you subscribed to Mantbyte.",
            f"Unsubscribe: {site_url}/verify?action=unsubscribe",
        ])

        return "\n".join(lines)
