"""
Agent 2: Research Agent
Collects and structures information from the selected topic.
Produces structured research, NOT article text.
"""

import sys
import os
import requests
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai import generate_json, render_prompt


def scrape_article_text(url: str) -> str:
    """Attempt to scrape the main text content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        # Get text
        text = soup.get_text(separator="\n")
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        
        # Limit to first 15,000 characters to fit context window reasonably
        return text[:15000]
    except Exception as e:
        print(f"    ⚠️ Failed to scrape full article text: {e}")
        return "Full text could not be scraped."


def research_topic(candidate: dict) -> dict:
    """
    Produce structured research for a selected topic.
    
    Args:
        candidate: A single candidate dict from trend_detector
    
    Returns:
        Structured research dict
    """
    link = candidate.get('link', '')
    
    print(f"  📚 Researching: {candidate.get('original_title', '')[:60]}...")
    print(f"    Fetching full text from {link}...")
    
    full_text = scrape_article_text(link) if link else "No URL provided."

    topic_context = (
        f"Title: {candidate.get('original_title', '')}\n"
        f"Source: {candidate.get('source', '')}\n"
        f"Link: {link}\n"
        f"Blog Angle: {candidate.get('blog_angle', '')}\n"
        f"Key Concepts: {', '.join(candidate.get('key_concepts', []))}\n\n"
        f"--- FULL ARTICLE CONTENT ---\n"
        f"{full_text}\n"
        f"----------------------------\n"
    )

    system_instruction = render_prompt("researcher.md")
    user_prompt = f"Research this topic thoroughly:\n\n{topic_context}"

    result = generate_json(
        agent_name="researcher",
        system_instruction=system_instruction,
        user_prompt=user_prompt,
        temperature=0.3,
    )

    # Attach original candidate metadata
    result["_candidate"] = candidate

    facts_count = len(result.get("key_facts", []))
    print(f"  ✅ Research complete: {facts_count} key facts collected")

    return result
