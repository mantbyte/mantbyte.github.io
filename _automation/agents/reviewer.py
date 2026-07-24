"""
Agent 10: Editorial Reviewer
Quality gate — checks the final article and decides PASS or FAIL.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat_json


REVIEW_PROMPT = """You are a senior editorial quality reviewer for Mantbyte, a technology blog.

Given a complete Markdown blog post (with frontmatter), evaluate its quality.

Check for:
1. Word count (should be 1500-4000 words for the body)
2. YAML frontmatter completeness (title, date, categories, excerpt, cover_image)
3. Proper Markdown formatting (headings, code blocks, lists)
4. No placeholder text like "[TODO]", "INSERT HERE", "Lorem ipsum"
5. No broken image references
6. Logical section flow
7. Technical accuracy (based on what's written)
8. Readability and engagement
9. No duplicate content sections
10. Professional tone

Score the article from 1-10:
- 9-10: Excellent, ready to publish
- 7-8: Good, minor improvements possible
- 5-6: Acceptable but needs editing
- 1-4: Below quality threshold, reject

Return JSON with this EXACT structure:
{
  "score": 8,
  "decision": "PASS" or "FAIL",
  "word_count": 2500,
  "frontmatter_valid": true,
  "issues": [
    {"type": "grammar|formatting|content|accuracy", "description": "...", "severity": "critical|warning|info"}
  ],
  "strengths": ["what's good about this article"],
  "summary": "One-paragraph quality assessment"
}
"""


def review_article(markdown_content: str, min_score: int = 7) -> dict:
    """
    Review the complete article for quality.
    
    Args:
        markdown_content: Complete Markdown file with frontmatter
        min_score: Minimum score to pass (default 7)
    
    Returns:
        Review result dict
    """
    # Basic pre-checks
    word_count = len(markdown_content.split())
    has_frontmatter = markdown_content.startswith("---")

    print(f"  🔬 Reviewing article ({word_count} words)...")

    if word_count < 500:
        return {
            "score": 1,
            "decision": "FAIL",
            "word_count": word_count,
            "frontmatter_valid": has_frontmatter,
            "issues": [{"type": "content", "description": "Article too short", "severity": "critical"}],
            "strengths": [],
            "summary": f"Article is only {word_count} words. Minimum is 1500.",
        }

    result = chat_json(
        messages=[
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": f"Review this article:\n\n{markdown_content}"},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.2,
    )

    score = result.get("score", 0)
    decision = "PASS" if score >= min_score else "FAIL"
    result["decision"] = decision

    issues = result.get("issues", [])
    critical = sum(1 for i in issues if i.get("severity") == "critical")

    print(f"  {'✅' if decision == 'PASS' else '❌'} Review: {decision} "
          f"(score: {score}/10, {len(issues)} issues, {critical} critical)")

    return result
