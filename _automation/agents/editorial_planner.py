"""
Agent 5: Editorial Planner
Creates a structured article outline with sections, learning objectives, and reading difficulty.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import generate_json, render_prompt
import json


def create_editorial_plan(verified_research: dict, knowledge_context: dict) -> dict:
    """
    Create a structured article outline.
    
    Args:
        verified_research: Cleaned research from fact_checker
        knowledge_context: Duplicate check results with internal link suggestions
    
    Returns:
        Editorial plan dict
    """
    cleaned = verified_research.get("cleaned_research", {})
    internal_links = knowledge_context.get("internal_links", [])

    context = (
        f"Topic: {cleaned.get('topic', 'Unknown')}\n"
        f"Summary: {cleaned.get('summary', '')}\n"
        f"Key Facts: {json.dumps(cleaned.get('key_facts', []))}\n"
        f"Technical Details: {json.dumps(cleaned.get('technical_details', {}))}\n"
        f"Impact: {cleaned.get('impact', '')}\n"
        f"Future Outlook: {cleaned.get('future_outlook', '')}\n"
        f"\nInternal links available for cross-referencing:\n"
    )

    for link in internal_links:
        context += f"- [{link.get('title', '')}]({link.get('url', '')})\n"

    print(f"  📋 Creating editorial plan...")

    system_instruction = render_prompt("planner.md")

    result = generate_json(
        agent_name="editorial_planner",
        system_instruction=system_instruction,
        user_prompt=context,
        temperature=0.5,
    )

    sections = result.get("sections", [])
    total_words = sum(s.get("word_count_target", 0) for s in sections)
    print(f"  ✅ Plan created: {len(sections)} sections, ~{total_words} words target")

    return result
