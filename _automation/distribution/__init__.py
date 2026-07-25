"""
Mantbyte Distribution Engine v1
Completely free distribution & subscriber notification system.

Architecture:
    Editorial Pipeline → distribution_event.json → Distribution Engine → Channels

Channels:
    - Push Notifications (FCM)
    - Newsletter (Firestore + SMTP)
    - Daily Digest (queued emails)
    - RSS Validation
"""

__version__ = "1.0.0"
