"""
Agent 3: Source Verification Agent
Verifies facts from the research, rejects unsupported claims.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat_json
import json


VERIFICATION_PROMPT = """You are a fact-checking editor for Mantbyte, a technology blog.

Given a structured research document, your job is to:
1. Review each fact and statistic for plausibility.
2. Flag any claims that seem fabricated, exaggerated, or unverifiable.
3. Mark each fact with a verification status.
4. Remove or flag any hallucinated data.

RULES:
- If a statistic seems too precise or too convenient, flag it as "unverified".
- If dates or version numbers don't make sense, correct them or flag them.
- If two facts contradict each other, highlight the conflict.
- NEVER add new facts that weren't in the research.
- Be conservative: when in doubt, flag as "needs_review".

Return JSON with this EXACT structure:
{
  "verification_passed": true|false,
  "overall_confidence": "high|medium|low",
  "verified_facts": [
    {"fact": "...", "status": "verified|unverified|rejected", "note": "..."}
  ],
  "flagged_issues": [
    {"issue": "...", "severity": "critical|warning|info"}
  ],
  "cleaned_research": {
    "topic": "...",
    "summary": "...",
    "key_facts": ["only verified facts here"],
    "technical_details": {},
    "impact": "...",
    "future_outlook": "..."
  }
}
"""


def verify_research(research: dict) -> dict:
    """
    Verify facts from the research document.
    
    Args:
        research: Structured research dict from researcher agent
    
    Returns:
        Verification result with cleaned research
    """
    # Prepare research for verification (exclude internal metadata)
    research_for_review = {k: v for k, v in research.items() if not k.startswith("_")}

    print(f"  ✅ Verifying research for: {research.get('topic', 'Unknown')[:60]}...")

    result = chat_json(
        messages=[
            {"role": "system", "content": VERIFICATION_PROMPT},
            {"role": "user", "content": f"Verify this research:\n\n{json.dumps(research_for_review, indent=2)}"},
        ],
        model="llama-3.1-8b-instant",
        temperature=0.2,
    )

    # Carry forward candidate metadata
    if "_candidate" in research:
        result["_candidate"] = research["_candidate"]

    passed = result.get("verification_passed", False)
    confidence = result.get("overall_confidence", "unknown")
    issues = len(result.get("flagged_issues", []))

    print(f"  {'✅' if passed else '❌'} Verification: {'PASSED' if passed else 'FAILED'} "
          f"(confidence: {confidence}, issues: {issues})")

    return result
