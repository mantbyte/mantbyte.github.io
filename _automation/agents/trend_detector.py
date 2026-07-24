"""
Agent 1: Trend Detection
Reads RSS feeds, scores news importance, and ranks potential blog topics.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat_json


SCORING_PROMPT = """You are a technical news editor for a technology blog called Mantbyte.
The blog covers: AI/ML, DevOps, Cloud Computing, Cybersecurity, Programming, and Geopolitics of Tech.

I will give you a list of recent news articles from RSS feeds.
Your job is to:
1. Score each article from 1-10 on its value as a potential blog post topic.
2. Consider: technical depth potential, reader interest, uniqueness, and timeliness.
3. Select the TOP 3 candidates.

Scoring criteria:
- 9-10: Major product launch, groundbreaking research, significant industry shift
- 7-8: Important update, interesting technical deep-dive potential
- 5-6: Moderately interesting, could work as a blog post
- 1-4: Low value, too niche, or purely promotional

For each top candidate, provide:
- The original title
- A suggested blog angle (how Mantbyte should cover it)
- Why it would make a good article
- Suggested category: Tech, News, or Geopolitics

Return JSON with this EXACT structure:
{
  "candidates": [
    {
      "rank": 1,
      "original_title": "...",
      "source": "...",
      "link": "...",
      "score": 9,
      "blog_angle": "...",
      "reasoning": "...",
      "category": "Tech",
      "key_concepts": ["concept1", "concept2"]
    }
  ]
}
"""


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

    result = chat_json(
        messages=[
            {"role": "system", "content": SCORING_PROMPT},
            {"role": "user", "content": f"Here are the recent articles:\n\n{articles_text}\n\nRank the top 3 candidates."},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.3,
    )

    # Validate output
    candidates = result.get("candidates", [])
    print(f"  ✅ Found {len(candidates)} trending topics")
    for c in candidates:
        print(f"    #{c.get('rank', '?')}: {c.get('original_title', 'Unknown')[:60]} (score: {c.get('score', '?')})")

    return result
