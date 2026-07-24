"""
Agent 7: SEO Optimizer
Generates SEO metadata: title, slug, description, tags, Open Graph data.
"""

import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import generate_json, render_prompt


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

    system_instruction = render_prompt("seo.md")
    user_prompt = (
        f"Title: {title}\n"
        f"Suggested Category: {category}\n\n"
        f"Article Preview:\n{preview}"
    )

    result = generate_json(
        agent_name="seo_optimizer",
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        temperature=0.3,
    )

    # Sanitize slug
    slug = result.get("slug", "")
    slug = re.sub(r"[^a-z0-9-]", "", slug.lower())
    slug = re.sub(r"-+", "-", slug).strip("-")
    result["slug"] = slug

    print(f"  ✅ SEO optimized: slug='{slug}', {len(result.get('tags', []))} tags")

    return result
