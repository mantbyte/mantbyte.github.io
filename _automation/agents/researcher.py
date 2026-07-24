"""
Agent 2: Research Agent
Collects and structures information from the selected topic.
Produces structured research, NOT article text.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.groq_client import chat_json


RESEARCH_PROMPT = """You are a senior technical researcher for Mantbyte, a technology blog.

Given a news article title, source, and summary, your job is to produce STRUCTURED RESEARCH that a writer will later use to write an original article.

You must:
1. Identify the key facts, technologies, and concepts involved.
2. Provide technical background and context.
3. List relevant statistics, version numbers, and dates.
4. Identify stakeholders, companies, and products involved.
5. Suggest comparisons or alternative technologies.
6. Note the broader impact and future implications.

IMPORTANT RULES:
- Do NOT write the article. Only provide raw research material.
- Do NOT fabricate statistics or benchmarks. If you are unsure, say "unverified" or "approximate".
- Include source attribution where possible.
- Be specific with technical details (versions, architectures, APIs).

Return JSON with this EXACT structure:
{
  "topic": "...",
  "summary": "2-3 sentence overview",
  "key_facts": [
    {"fact": "...", "source": "...", "confidence": "high|medium|low"}
  ],
  "technical_details": {
    "technologies": ["..."],
    "versions": ["..."],
    "architecture": "...",
    "key_concepts": ["..."]
  },
  "stakeholders": ["company or person names"],
  "statistics": [
    {"metric": "...", "value": "...", "source": "...", "verified": true|false}
  ],
  "comparisons": [
    {"vs": "...", "advantage": "...", "disadvantage": "..."}
  ],
  "impact": "...",
  "future_outlook": "...",
  "suggested_sections": ["section title ideas for the article"]
}
"""


def research_topic(candidate: dict) -> dict:
    """
    Produce structured research for a selected topic.
    
    Args:
        candidate: A single candidate dict from trend_detector
    
    Returns:
        Structured research dict
    """
    topic_context = (
        f"Title: {candidate.get('original_title', '')}\n"
        f"Source: {candidate.get('source', '')}\n"
        f"Link: {candidate.get('link', '')}\n"
        f"Blog Angle: {candidate.get('blog_angle', '')}\n"
        f"Key Concepts: {', '.join(candidate.get('key_concepts', []))}"
    )

    print(f"  📚 Researching: {candidate.get('original_title', '')[:60]}...")

    result = chat_json(
        messages=[
            {"role": "system", "content": RESEARCH_PROMPT},
            {"role": "user", "content": f"Research this topic thoroughly:\n\n{topic_context}"},
        ],
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=4096,
    )

    # Attach original candidate metadata
    result["_candidate"] = candidate

    facts_count = len(result.get("key_facts", []))
    print(f"  ✅ Research complete: {facts_count} key facts collected")

    return result
