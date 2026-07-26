"""
Channel: RSS Validator

Validates the site's RSS feed after article publication.
This is a passive channel — it doesn't send notifications,
but ensures the RSS feed is correctly structured.
"""

import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.error import URLError

from distribution.channels.base import ChannelInterface, DistributionResult


class RSSValidatorChannel(ChannelInterface):
    """Validates the RSS feed after publication."""

    def __init__(self, config: dict):
        self.config = config
        self.site_url = config.get("site_url", "https://mantbyte.github.io")

    @property
    def name(self) -> str:
        return "rss"

    def is_enabled(self, config: dict) -> bool:
        return config.get("enable_rss_validation", True)

    def distribute(self, article_event: dict) -> DistributionResult:
        """
        Validate the RSS feed contains the newly published article.

        This is a best-effort check. It fetches the live feed.xml
        and looks for the article title. If the site hasn't deployed yet,
        the check will gracefully skip.
        """
        feed_url = f"{self.site_url.rstrip('/')}/feed.xml"
        title = article_event.get("title", "")

        print(f"  📡 RSS Validation: Checking {feed_url}")

        try:
            req = Request(feed_url, headers={"User-Agent": "Mantbyte-RSS-Validator/1.0"})
            with urlopen(req, timeout=15) as response:
                feed_xml = response.read().decode("utf-8")
        except URLError as e:
            print(f"  ⚠️ Could not fetch RSS feed (site may not be deployed yet): {e}")
            return DistributionResult(
                channel=self.name,
                status="skipped",
                details={"reason": "Feed not reachable", "error": str(e)},
            )
        except Exception as e:
            return DistributionResult(
                channel=self.name,
                status="failed",
                error=str(e),
            )

        # Validate XML structure
        issues = []
        try:
            root = ET.fromstring(feed_xml)
        except ET.ParseError as e:
            return DistributionResult(
                channel=self.name,
                status="failed",
                error=f"RSS XML parse error: {e}",
            )

        # Check required elements
        channel = root.find("channel") or root.find("{http://www.w3.org/2005/Atom}feed")
        if channel is None:
            issues.append("Missing <channel> element")

        # Check for items
        items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
        if not items:
            issues.append("No <item> elements found in feed")
        else:
            # Check if the new article exists
            article_found = False
            for item in items:
                item_title_el = item.find("title") or item.find("{http://www.w3.org/2005/Atom}title")
                if item_title_el is not None and title and title.lower() in (item_title_el.text or "").lower():
                    article_found = True
                    break

            if not article_found and title:
                issues.append(f"New article '{title[:50]}...' not found in feed (may need deployment)")

            # Validate first item has required fields
            first_item = items[0]
            for required in ["title", "link", "description", "pubDate"]:
                el = first_item.find(required)
                if el is None or not (el.text or "").strip():
                    issues.append(f"First item missing <{required}>")

        if issues:
            print(f"  ⚠️ RSS issues found: {'; '.join(issues)}")
            return DistributionResult(
                channel=self.name,
                status="partial",
                details={"issues": issues, "item_count": len(items)},
            )

        print(f"  ✅ RSS feed valid ({len(items)} items)")
        return DistributionResult(
            channel=self.name,
            status="success",
            sent_count=len(items),
            details={"item_count": len(items), "article_found": True},
        )
