"""
Agent 4: Knowledge Base Agent
Tracks published articles, prevents duplicates, suggests internal links.
Uses a simple JSON file stored in _data/knowledge.json.
"""

import os
import json
from datetime import datetime, timezone


KNOWLEDGE_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "_data",
    "knowledge.json",
)


def load_knowledge() -> dict:
    """Load the knowledge base from disk."""
    if os.path.exists(KNOWLEDGE_FILE):
        with open(KNOWLEDGE_FILE, "r") as f:
            return json.load(f)
    return {"published_articles": [], "last_updated": None}


def save_knowledge(knowledge: dict):
    """Save the knowledge base to disk."""
    knowledge["last_updated"] = datetime.now(timezone.utc).isoformat()
    os.makedirs(os.path.dirname(KNOWLEDGE_FILE), exist_ok=True)
    with open(KNOWLEDGE_FILE, "w") as f:
        json.dump(knowledge, f, indent=2)
    print(f"  💾 Knowledge base updated ({len(knowledge['published_articles'])} articles tracked)")


def check_duplicate(topic: str, key_concepts: list, knowledge: dict = None) -> dict:
    """
    Check if a topic has already been covered.
    
    Args:
        topic: The proposed article topic/title
        key_concepts: List of key concepts from the research
        knowledge: Optional pre-loaded knowledge dict
    
    Returns:
        Dict with is_duplicate, similar_articles, and internal_links
    """
    if knowledge is None:
        knowledge = load_knowledge()

    published = knowledge.get("published_articles", [])
    topic_lower = topic.lower()
    concepts_lower = set(c.lower() for c in key_concepts)

    similar_articles = []
    internal_links = []

    for article in published:
        article_title = article.get("title", "").lower()
        article_topics = set(t.lower() for t in article.get("key_topics", []))

        # Check title similarity
        title_words = set(topic_lower.split())
        article_words = set(article_title.split())
        common_words = title_words & article_words
        # Exclude common stopwords
        stopwords = {"the", "a", "an", "is", "of", "in", "to", "and", "for", "on", "with", "how", "what", "why"}
        meaningful_common = common_words - stopwords

        # Check concept overlap
        concept_overlap = concepts_lower & article_topics

        similarity = len(meaningful_common) / max(len(title_words - stopwords), 1)

        if similarity > 0.5 or len(concept_overlap) >= 2:
            similar_articles.append({
                "title": article.get("title"),
                "slug": article.get("slug"),
                "similarity": round(similarity, 2),
                "shared_concepts": list(concept_overlap),
            })

        # Suggest internal links for related (but not duplicate) articles
        if 0.1 < similarity <= 0.5 or len(concept_overlap) == 1:
            url = article.get("url", "")
            if url:
                internal_links.append({
                    "title": article.get("title"),
                    "url": url,
                })

    is_duplicate = any(s["similarity"] > 0.6 for s in similar_articles)

    print(f"  🧠 Knowledge check: {'DUPLICATE' if is_duplicate else 'UNIQUE'} "
          f"({len(similar_articles)} similar, {len(internal_links)} link suggestions)")

    return {
        "is_duplicate": is_duplicate,
        "similar_articles": similar_articles,
        "internal_links": internal_links[:5],  # Max 5 suggestions
    }


def add_article(title: str, slug: str, date: str, category: str, key_topics: list, url: str):
    """Add a newly published article to the knowledge base."""
    knowledge = load_knowledge()

    knowledge["published_articles"].append({
        "title": title,
        "slug": slug,
        "date": date,
        "category": category,
        "key_topics": key_topics,
        "url": url,
    })

    save_knowledge(knowledge)
