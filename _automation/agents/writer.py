"""
Agent 6: Technical Writer
Writes the actual article using verified research and the editorial plan.
Produces Markdown body content (no frontmatter).
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat
import json


WRITING_PROMPT = """You are a senior technical writer at Mantbyte, a technology blog run by Sujal Lohar, a Computer Science student.

Your writing style:
- Clear, confident, and educational
- You explain complex concepts in an accessible way
- You use real examples and practical comparisons
- You avoid hype and marketing language
- You write like you're explaining something interesting to a smart colleague
- You use Markdown formatting: ## headings, **bold**, `code`, bullet lists, > blockquotes

RULES:
1. Write ONLY the article body in Markdown format. Do NOT include YAML frontmatter.
2. Do NOT start with a level-1 heading (#). The title is handled separately.
3. Start directly with the introduction paragraph.
4. Use ## for major section headings and ### for subsections.
5. Target 2000-3500 words.
6. Include code examples where relevant (use fenced code blocks with language).
7. Include comparison tables where appropriate.
8. Do NOT copy or closely paraphrase any single source — synthesize from multiple inputs.
9. Use the internal links provided naturally within the text where relevant.
10. End with a forward-looking conclusion.
11. Every claim should be traceable to the provided research. Do NOT add unverified facts.
"""


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

    article_body = chat(
        messages=[
            {"role": "system", "content": WRITING_PROMPT},
            {"role": "user", "content": f"Write the complete article based on this brief:\n\n{brief}"},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=8000,
    )

    word_count = len(article_body.split())
    print(f"  ✅ Article written: {word_count} words")

    return article_body
