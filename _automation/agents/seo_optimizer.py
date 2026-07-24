"""
Agent 7: SEO Optimizer
Generates SEO metadata: title, slug, description, tags, Open Graph data.
"""

import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat_json


SEO_PROMPT = """You are an SEO specialist for Mantbyte (mantbyte.github.io), a technology blog.

Given an article title and the first 500 words of the article, generate optimized SEO metadata.

RULES:
- SEO title should be 50-60 characters, compelling, and include primary keyword.
- Meta description should be 150-160 characters, include a call-to-action.
- Slug should be lowercase, hyphenated, max 6 words, no stop words.
- Excerpt should be 1-2 sentences that hook the reader.
- Tags should be 4-8 relevant technical keywords.
- Category must be exactly one of: Tech, News, Geopolitics.

Return JSON with this EXACT structure:
{
  "seo_title": "...",
  "slug": "lowercase-hyphenated-slug",
  "meta_description": "...",
  "excerpt": "...",
  "category": "Tech",
  "tags": ["tag1", "tag2"],
  "og_description": "...",
  "cover_caption": "A one-line caption describing the cover image"
}
"""


def optimize_seo(title: str, article_body: str, category: str = "Tech") -> dict:
    """
    Generate SEO-optimized metadata for the article.
    
    Args:
        title: Article title from editorial plan
        article_body: First portion of the article text
        category: Suggested category
    
    Returns:
        SEO metadata dict
    """
    # Use first 500 words for context
    preview = " ".join(article_body.split()[:500])

    print(f"  🔎 Optimizing SEO...")

    result = chat_json(
        messages=[
            {"role": "system", "content": SEO_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Title: {title}\n"
                    f"Suggested Category: {category}\n\n"
                    f"Article Preview:\n{preview}"
                ),
            },
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3,
    )

    # Sanitize slug
    slug = result.get("slug", "")
    slug = re.sub(r"[^a-z0-9-]", "", slug.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    result["slug"] = slug

    print(f"  ✅ SEO optimized: slug='{slug}', {len(result.get('tags', []))} tags")

    return result
