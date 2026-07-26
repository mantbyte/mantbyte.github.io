"""
Distribution Engine — Email Verification (Double Opt-In)

Handles the complete verification flow:
1. Generate unique verification token
2. Send verification email via SMTP
3. Verification page on the site confirms via Firestore client-side
"""

import uuid
import hashlib
from datetime import datetime
from typing import Optional


VERIFICATION_EMAIL_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify your Mantbyte subscription</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8f9fa; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 0;">
                <table role="presentation" style="width: 560px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 24px; text-align: center; border-bottom: 1px solid #eaeaea;">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 700; color: #111111; letter-spacing: -0.5px;">mantbyte</h1>
                        </td>
                    </tr>
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 600; color: #111111;">Confirm your subscription</h2>
                            <p style="margin: 0 0 24px; font-size: 15px; line-height: 1.6; color: #555555;">
                                Thanks for subscribing to Mantbyte! Please verify your email address to start receiving technical articles and insights.
                            </p>
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td style="text-align: center; padding: 8px 0 32px;">
                                        <a href="{verification_url}"
                                           style="display: inline-block; padding: 14px 32px; background-color: #111111; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 15px; letter-spacing: 0.3px;">
                                            Verify Email Address
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            <p style="margin: 0 0 8px; font-size: 13px; color: #999999;">
                                If you didn't subscribe to Mantbyte, you can safely ignore this email.
                            </p>
                            <p style="margin: 0; font-size: 13px; color: #999999;">
                                This link expires in 48 hours.
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; background-color: #fafafa; border-top: 1px solid #eaeaea; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #999999;">
                                Mantbyte &middot; Engineering insights & technical deep dives
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


VERIFICATION_TEXT_TEMPLATE = """Confirm your Mantbyte subscription

Thanks for subscribing to Mantbyte!

Please verify your email by visiting:
{verification_url}

If you didn't subscribe, you can safely ignore this email.
This link expires in 48 hours.

— Mantbyte"""


def generate_verification_token(email: str) -> str:
    """
    Generate a unique, deterministic-ish verification token.

    Uses UUID4 for uniqueness, but also hashes the email to make
    the token partially deterministic (same email always gets a
    consistent prefix for debugging).

    Args:
        email: Subscriber email address.

    Returns:
        Verification token string.
    """
    email_hash = hashlib.sha256(email.lower().strip().encode()).hexdigest()[:8]
    unique_id = uuid.uuid4().hex[:24]
    return f"{email_hash}-{unique_id}"


def send_verification_email(
    email: str,
    token: str,
    site_url: str,
    email_provider, # Type EmailProvider, but avoiding import loop here
    from_name: str = "Mantbyte",
) -> bool:
    """
    Send a double opt-in verification email, if a provider is configured.

    Args:
        email: Subscriber email address.
        token: Verification token.
        site_url: Base URL of the site (e.g., https://mantbyte.github.io).
        email_provider: Configured EmailProvider instance (or None).
        from_name: Display name for the sender.

    Returns:
        True if email sent successfully or skipped intentionally.
    """
    if not email_provider:
        print(f"  ⏭️ No EmailProvider configured. Skipping verification email to {email[:3]}***")
        # Returning True because this is the intended fallback behavior,
        # so the system doesn't treat it as a failure.
        return True

    success = email_provider.send_verification(
        to_email=email,
        token=token,
        site_url=site_url,
        from_name=from_name,
    )

    if success:
        print(f"  ✉️ Verification email sent to {email[:3]}***")
    else:
        print(f"  ❌ Failed to send verification email to {email[:3]}***")

    return success


def store_subscriber(
    db,
    email: str,
    token: str,
    categories: Optional[list] = None,
) -> bool:
    """
    Store a new newsletter subscriber in Firestore.
    Note: Usually this happens client-side now, but keeping this
    for backend flexibility.

    Args:
        db: Firestore client.
        email: Subscriber email.
        token: Verification token.
        categories: Optional list of preferred categories.

    Returns:
        True if stored (not a duplicate).
    """
    if not db:
        print("  ⚠️ Firestore not available. Cannot store subscriber.")
        return False

    try:
        collection = db.collection("subscribers")

        # Check for duplicate
        existing = collection.where("email", "==", email.lower().strip()).limit(1).get()
        if len(list(existing)) > 0:
            print(f"  ℹ️ Subscriber {email[:3]}*** already exists.")
            return False

        # Use the verification capability as the document ID. The static
        # verification page can then update this exact document without a
        # public subscriber query.
        collection.document(token).set({
            "email": email.lower().strip(),
            "verified": False,
            "created_at": datetime.utcnow().isoformat(),
            "last_seen": datetime.utcnow().isoformat(),
            "is_active": True,
            "notification_enabled": True,
            "newsletter_enabled": True,
            "push_enabled": False,
            "preferences": {
                "categories": categories or [],
            },
            "verification_token": token,
        })

        print(f"  ✅ Subscriber {email[:3]}*** stored (pending verification).")
        return True

    except Exception as e:
        print(f"  ❌ Failed to store subscriber: {e}")
        return False
