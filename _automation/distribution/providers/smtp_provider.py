"""
SMTP Implementation of EmailProvider

Uses Python's built-in smtplib to send emails.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from typing import Optional

from distribution.providers.base import EmailProvider
from distribution.email_verification import VERIFICATION_EMAIL_TEMPLATE, VERIFICATION_TEXT_TEMPLATE


class SMTPEmailProvider(EmailProvider):
    """
    Sends emails via SMTP (e.g., Gmail with App Passwords).
    """

    def __init__(self, config: dict):
        """
        Args:
            config: Dict containing:
                smtp_host, smtp_port, smtp_email, smtp_password, smtp_use_tls
        """
        self.host = config.get("smtp_host", "smtp.gmail.com")
        self.port = int(config.get("smtp_port", 587))
        self.email = config.get("smtp_email", "")
        self.password = config.get("smtp_password", "")
        self.use_tls = str(config.get("smtp_use_tls", "True")).lower() in ("true", "1", "yes")

        if not self.email or not self.password:
            raise ValueError("SMTP_EMAIL and SMTP_PASSWORD must be provided for SMTPEmailProvider.")

    def send_verification(
        self,
        to_email: str,
        token: str,
        site_url: str,
        from_name: str = "Mantbyte"
    ) -> bool:
        verification_url = f"{site_url.rstrip('/')}/verify?token={token}&email={to_email}"
        html_body = VERIFICATION_EMAIL_TEMPLATE.replace("{verification_url}", verification_url)
        text_body = VERIFICATION_TEXT_TEMPLATE.replace("{verification_url}", verification_url)

        return self._send_single(
            to_email=to_email,
            subject="Verify your Mantbyte subscription",
            html_body=html_body,
            text_body=text_body,
            from_name=from_name
        )

    def send_digest(
        self,
        recipients: list[str],
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        from_name: str = "Mantbyte"
    ) -> dict:
        sent = 0
        failed = 0

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.email, self.password)

                for recipient in recipients:
                    try:
                        msg = MIMEMultipart("alternative")
                        msg["Subject"] = subject
                        msg["From"] = formataddr((from_name, self.email))
                        msg["To"] = recipient
                        msg["Date"] = formatdate(localtime=True)
                        msg["List-Unsubscribe"] = f"<mailto:{self.email}?subject=unsubscribe>"

                        if text_body:
                            msg.attach(MIMEText(text_body, "plain", "utf-8"))
                        msg.attach(MIMEText(html_body, "html", "utf-8"))

                        server.sendmail(self.email, recipient, msg.as_string())
                        sent += 1
                    except Exception as e:
                        print(f"  ⚠️ Failed to send to {recipient}: {e}")
                        failed += 1

        except Exception as e:
            print(f"  ❌ SMTP connection error during batch send: {e}")
            failed = len(recipients) - sent

        return {"sent": sent, "failed": failed}

    def send_welcome(self, to_email: str, site_url: str, from_name: str = "Mantbyte") -> bool:
        # Placeholder for future welcome email
        return True

    def _send_single(self, to_email: str, subject: str, html_body: str, text_body: str, from_name: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((from_name, self.email))
            msg["To"] = to_email
            msg["Date"] = formatdate(localtime=True)

            msg.attach(MIMEText(text_body, "plain", "utf-8"))
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.email, self.password)
                server.sendmail(self.email, to_email, msg.as_string())

            return True
        except Exception as e:
            print(f"  ❌ Email send failed to {to_email}: {e}")
            return False
