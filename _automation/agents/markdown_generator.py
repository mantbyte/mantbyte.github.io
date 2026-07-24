"""
Agent 9: Markdown Generator
Assembles the final production-ready Markdown file with YAML frontmatter.
"""

from datetime import datetime, timezone, timedelta


def generate_markdown(
    title: str,
    article_body: str,
    seo_data: dict,
    image_data: dict,
    date: datetime = None,
) -> str:
    """
    Assemble the complete Markdown file.
    
    Args:
        title: Article title
        article_body: Markdown body from the writer agent
        seo_data: SEO metadata from the seo_optimizer
        image_data: Image paths from the image_generator
        date: Publication date (defaults to now)
    
    Returns:
        Complete Markdown file content as a string
    """
    if date is None:
        # Use IST (UTC+5:30)
        ist = timezone(timedelta(hours=5, minutes=30))
        date = datetime.now(ist)

    date_str = date.strftime("%Y-%m-%d %H:%M:%S %z")
    category = seo_data.get("category", "Tech")
    excerpt = seo_data.get("excerpt", "")
    cover_image = image_data.get("image_path", "")
    cover_caption = seo_data.get("cover_caption", "")

    # Build YAML frontmatter
    frontmatter = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: {category}
excerpt: "{excerpt}"
cover_image: "{cover_image}"
cover_caption: "{cover_caption}"
---"""

    # Assemble complete file
    markdown = f"{frontmatter}\n\n{article_body}\n"

    print(f"  📝 Markdown generated: {len(markdown)} bytes")

    return markdown


def get_filename(slug: str, date: datetime = None) -> str:
    """
    Generate the Jekyll-compatible filename.
    
    Args:
        slug: URL-friendly slug
        date: Publication date
    
    Returns:
        Filename like 2026-07-24-slug-here.md
    """
    if date is None:
        ist = timezone(timedelta(hours=5, minutes=30))
        date = datetime.now(ist)

    date_prefix = date.strftime("%Y-%m-%d")
    return f"{date_prefix}-{slug}.md"
