"""
Channel Interface — Base class for all distribution channels.

Every distribution channel must implement this interface.
Adding a new channel (Telegram, Discord, etc.) requires only:
1. Create a new file in channels/
2. Subclass ChannelInterface
3. Implement distribute() and is_enabled()

No existing code needs modification.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class DistributionResult:
    """Result of a channel distribution attempt."""
    channel: str
    status: str  # "success", "failed", "partial", "skipped"
    sent_count: int = 0
    failed_count: int = 0
    error: Optional[str] = None
    details: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def is_success(self) -> bool:
        return self.status in ("success", "partial")


class ChannelInterface(ABC):
    """
    Abstract base class for distribution channels.

    Every channel must implement:
        - name: A unique identifier string
        - distribute(event): Send notification for the given article event
        - is_enabled(config): Whether this channel is active
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique channel identifier (e.g., 'push', 'newsletter', 'rss')."""
        ...

    @abstractmethod
    def distribute(self, article_event: dict) -> DistributionResult:
        """
        Execute distribution for a single article event.

        Args:
            article_event: Dict containing article metadata:
                - event: str ("article_published")
                - title: str
                - slug: str
                - category: str
                - excerpt: str
                - url: str
                - cover_image: str
                - tags: list[str]
                - published_at: str (ISO 8601)
                - filename: str

        Returns:
            DistributionResult with status and metrics.
        """
        ...

    @abstractmethod
    def is_enabled(self, config: dict) -> bool:
        """
        Check if this channel is enabled in the configuration.

        Args:
            config: The distribution_config dict.

        Returns:
            True if this channel should be active.
        """
        ...

    def __repr__(self) -> str:
        return f"<Channel: {self.name}>"
