"""
EmailProvider Interface

Abstract base class for all email delivery providers.
The Distribution Engine relies ONLY on this interface, never on a specific implementation.
If no EmailProvider is configured, the system still functions 100% normally (email delivery is just skipped).
"""

from abc import ABC, abstractmethod
from typing import Optional


class EmailProvider(ABC):
    """
    Interface for sending emails.
    Implementations could be SMTP, SendGrid, Mailgun, AWS SES, etc.
    """

    @abstractmethod
    def send_verification(
        self,
        to_email: str,
        token: str,
        site_url: str,
        from_name: str = "Mantbyte"
    ) -> bool:
        """
        Send a double opt-in verification email.

        Args:
            to_email: Recipient email address.
            token: Verification token.
            site_url: Base URL of the site.
            from_name: Sender display name.

        Returns:
            True if sent successfully, False otherwise.
        """
        ...

    @abstractmethod
    def send_digest(
        self,
        recipients: list[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_name: str = "Mantbyte"
    ) -> dict:
        """
        Send a compiled daily digest to multiple recipients.

        Args:
            recipients: List of subscriber email addresses.
            subject: Email subject.
            html_body: HTML digest content.
            text_body: Plaintext digest content.
            from_name: Sender display name.

        Returns:
            Dict containing {"sent": int, "failed": int}
        """
        ...

    @abstractmethod
    def send_welcome(
        self,
        to_email: str,
        site_url: str,
        from_name: str = "Mantbyte"
    ) -> bool:
        """
        Send a welcome email upon successful verification.
        """
        ...
