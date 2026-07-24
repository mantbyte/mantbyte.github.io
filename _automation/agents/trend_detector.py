"""
Agent 1: Trend Detection
Reads RSS feeds, scores news importance, and ranks potential blog topics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import generate_json, render_prompt


def detect_trends(articles: list) -> dict:
    """
    Score and rank articles to find the best blog topic.
    
    Args:
        articles: List of normalized RSS articles from rss_reader
    
    Returns:
        Dict with ranked candidates
    """
    if not articles:
        print("  ❌ No articles to analyze")
        return {"candidates": []}

    # Build article summary for the LLM
    # Limit to 40 articles to fit context
    article_summaries = []
    for i, article in enumerate(articles[:40]):
        article_summaries.append(
            f"{i+1}. [{article['source']}] {article['title']}\n"
            f"   Summary: {article['summary'][:200]}\n"
            f"   Link: {article['link']}"
        )

    articles_text = "\n\n".join(article_summaries)

    print(f"  🔍 Analyzing {len(article_summaries)} articles for trends...")

    system_instruction = render_prompt("trend_detector.md")
    user_prompt = f"Here are the recent articles:\n\n{articles_text}\n\nRank the top 3 candidates."

    result = generate_json(
        agent_name="trend_detector",
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        temperature=0.3,
    )

    # Validate output
    candidates = result.get("candidates", [])
    print(f"  ✅ Found {len(candidates)} trending topics")
    for c in candidates:
        print(f"    #{c.get('rank', '?')}: {c.get('original_title', 'Unknown')[:60]} (score: {c.get('score', '?')})")

    return result
