"""
Agent 6: Technical Writer
Writes the actual article using verified research and the editorial plan.
Produces Markdown body content (no frontmatter).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import generate_markdown, render_prompt
import json


def write_article(editorial_plan: dict, verified_research: dict) -> str:
    """
    Write the full article body in Markdown.
    
    Args:
        editorial_plan: Structured outline from editorial_planner
        verified_research: Cleaned research from fact_checker
    
    Returns:
        Article body as a Markdown string
    """
    cleaned = verified_research.get("cleaned_research", {})

    # Build the writing brief
    brief = (
        f"## Writing Brief\n\n"
        f"**Title:** {editorial_plan.get('title', '')}\n"
        f"**Target Audience:** {editorial_plan.get('target_audience', '')}\n"
        f"**Reading Level:** {editorial_plan.get('reading_level', '')}\n"
        f"**Tone:** {editorial_plan.get('tone', '')}\n\n"
        f"## Article Outline\n\n"
    )

    for i, section in enumerate(editorial_plan.get("sections", []), 1):
        brief += (
            f"{i}. **{section.get('heading', '')}** (~{section.get('word_count_target', 300)} words)\n"
            f"   Purpose: {section.get('purpose', '')}\n"
            f"   Key points: {', '.join(section.get('key_points', []))}\n\n"
        )

    brief += f"\n## Research Material\n\n{json.dumps(cleaned, indent=2)}\n"

    internal_links = editorial_plan.get("internal_links_to_include", [])
    if internal_links:
        brief += f"\n## Internal Links to Include\n\n"
        for link in internal_links:
            brief += f"- {link}\n"

    print(f"  ✍️ Writing article: {editorial_plan.get('title', '')[:60]}...")

    system_instruction = render_prompt("writer.md")
    user_prompt = f"Write the complete article based on this brief:\n\n{brief}"

    article_body = generate_markdown(
        agent_name="writer",
        system_instruction=system_instruction,
        user_prompt=user_prompt,
    )

    word_count = len(article_body.split())
    print(f"  ✅ Article written: {word_count} words")

    return article_body
