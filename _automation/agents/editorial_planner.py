"""
Agent 5: Editorial Planner
Creates a structured article outline with sections, learning objectives, and reading difficulty.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat_json
import json


PLANNING_PROMPT = """You are a senior technical editor at Mantbyte, a technology blog.

Given verified research and internal linking suggestions, create a detailed article outline.

The article should:
- Be 2000-3500 words total
- Start with a compelling introduction that hooks the reader
- Progress logically from concepts to implementation to impact
- Include practical examples, comparisons, and best practices
- End with a future outlook section
- Be accessible to intermediate developers while maintaining technical depth

Return JSON with this EXACT structure:
{
  "title": "Compelling, SEO-friendly article title",
  "subtitle": "Optional subtitle for extra context",
  "target_audience": "who this article is for",
  "reading_level": "beginner|intermediate|advanced",
  "estimated_read_time": "X min",
  "learning_objectives": ["what the reader will learn"],
  "sections": [
    {
      "heading": "Section Title",
      "purpose": "What this section accomplishes",
      "key_points": ["point 1", "point 2"],
      "word_count_target": 300,
      "include_example": true|false,
      "include_diagram": true|false
    }
  ],
  "internal_links_to_include": ["url1", "url2"],
  "tone": "informative yet engaging, like explaining to a smart colleague"
}
"""


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

    result = chat_json(
        messages=[
            {"role": "system", "content": PLANNING_PROMPT},
            {"role": "user", "content": context},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.5,
    )

    sections = result.get("sections", [])
    total_words = sum(s.get("word_count_target", 0) for s in sections)
    print(f"  ✅ Plan created: {len(sections)} sections, ~{total_words} words target")

    return result
