"""
Agent 10: Editorial Reviewer
Quality gate — checks the final article and decides PASS or FAIL.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import review, render_prompt


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

    system_instruction = render_prompt("reviewer.md")
    user_prompt = f"Review this article:\n\n{markdown_content}"

    result = review(
        agent_name="reviewer",
        system_instruction=system_instruction,
        user_prompt=user_prompt,
    )

    score = result.get("score", 0)
    decision = "PASS" if score >= min_score else "FAIL"
    result["decision"] = decision

    issues = result.get("issues", [])
    critical = sum(1 for i in issues if i.get("severity") == "critical")

    print(f"  {'✅' if decision == 'PASS' else '❌'} Review: {decision} "
          f"(score: {score}/10, {len(issues)} issues, {critical} critical)")

    return result
