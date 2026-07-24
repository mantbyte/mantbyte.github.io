"""
Agent 3: Source Verification Agent
Verifies facts from the research, rejects unsupported claims.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import generate_json, render_prompt
import json


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

    system_instruction = render_prompt("fact_checker.md")
    user_prompt = f"Verify this research:\n\n{json.dumps(research_for_review, indent=2)}"

    result = generate_json(
        agent_name="fact_checker",
        system_instruction=system_instruction,
        user_prompt=user_prompt,
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
