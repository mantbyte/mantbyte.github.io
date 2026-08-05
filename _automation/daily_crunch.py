"""
Mantbyte Daily Crunch Pipeline

Generates ultra-efficient daily digest articles (World, India, Finance, Spiritual) 
using minimal API calls (1 per article) to stay within free tier limits.
"""

import sys
import os
import json
import argparse
import datetime
from pathlib import Path

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.rss_reader import fetch_feeds
from _ai.provider import generate, generate_json
from utils.image_client import generate_cover_image
from agents.markdown_generator import generate_markdown, get_filename


def load_config() -> dict:
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def run_news_crunch(mode: str, dry_run: bool):
    """Generate a digest article from RSS feeds."""
    config = load_config()
    
    if mode == "world":
        feeds = config.get("world_news_feeds", [])
        title_prefix = "World News Crunch"
        category = "Geopolitics"
        prompt_topic = "Global News and World Events"
    elif mode == "india":
        feeds = config.get("india_news_feeds", [])
        title_prefix = "India News Crunch"
        category = "Geopolitics"
        prompt_topic = "Indian National News and Events"
    elif mode == "finance":
        feeds = config.get("finance_news_feeds", [])
        title_prefix = "Finance & Markets Crunch"
        category = "Tech"  # fallback category
        prompt_topic = "Global Finance, Economics, and Markets"
    else:
        raise ValueError(f"Unknown news mode: {mode}")

    print(f"📡 Fetching RSS feeds for {mode}...")
    articles = fetch_feeds(feeds, max_age_hours=24)
    
    if not articles:
        print(f"❌ No articles found for {mode}. Exiting.")
        return

    # Take top 20 distinct articles
    top_articles = articles[:20]
    
    # Build a consolidated text of the headlines
    news_text = ""
    for i, a in enumerate(top_articles, 1):
        news_text += f"{i}. Title: {a['title']}\nSource: {a['source']}\nSummary: {a['summary'][:200]}...\n\n"

    system_instruction = (
        f"You are a professional, objective, and analytical journalist writing for Mantbyte. "
        f"Your task is to write a highly engaging 'Daily Digest' article summarizing the top news items provided. "
        f"Do not invent news; only use the provided items. "
        f"Group the news logically into 3-4 sections with markdown headings. "
        f"Write in a clean, authoritative tone. Do not use conversational filler like 'Here is your digest'."
    )
    
    user_prompt = (
        f"Please write today's {prompt_topic} digest based on these items:\n\n{news_text}\n\n"
        f"Format as a complete article body in Markdown."
    )

    print(f"🤖 Generating {mode} article via Gemini...")
    if dry_run:
        article_body = f"Dry run article body for {mode}."
    else:
        article_body = generate("DailyCrunch", system_instruction, user_prompt, temperature=0.5)

    today_str = datetime.datetime.now().strftime("%B %d, %Y")
    title = f"{title_prefix}: {today_str}"
    slug = f"{mode}-news-crunch-{datetime.datetime.now().strftime('%Y-%m-%d')}"

    # Generate Image
    print(f"🎨 Generating cover image...")
    image_prompt = f"Abstract highly professional editorial illustration representing {prompt_topic}. Clean vector style, professional colors, no text."
    
    if dry_run:
        image_data = {
            "image_path": "/assets/images/posts/default-cover.png",
            "abs_path": None,
            "alt_text": f"Cover image for {title}",
            "generated": False,
        }
    else:
        abs_path = os.path.join(PROJECT_ROOT, "assets", "images", "posts", f"{slug}-cover.png")
        rel_path = f"/assets/images/posts/{slug}-cover.png"
        res_path = generate_cover_image(image_prompt, abs_path)
        
        image_data = {
            "image_path": rel_path if res_path else "/assets/images/posts/default-cover.png",
            "abs_path": abs_path if res_path else None,
            "alt_text": f"Cover image for {title}",
            "generated": bool(res_path),
        }

    seo_data = {
        "slug": slug,
        "excerpt": f"Your daily 2-minute digest covering the most important {prompt_topic.lower()} from around the globe.",
        "category": category,
        "tags": [mode, "news", "digest"]
    }

    markdown = generate_markdown(title, article_body, seo_data, image_data)
    
    _save_article(markdown, slug, dry_run)


def run_spiritual_crunch(dry_run: bool):
    """Generate a unique philosophical/spiritual story."""
    history_file = os.path.join(PROJECT_ROOT, "_data", "spiritual_history.json")
    
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
    except Exception:
        history = []

    history_text = "\n".join([f"- {h}" for h in history])
    
    system_instruction = (
        "You are a wise philosopher and storyteller. Your task is to write a standalone, "
        "engaging philosophical or spiritual article based on classical world or Indian texts "
        "(e.g., Upanishads, Stoicism, Zen, Bhagavad Gita, Tao Te Ching). "
        "The article should tell a brief story or explain a core concept, followed by how it applies to modern life. "
        "Do not write conversational filler."
    )
    
    user_prompt = (
        f"Please write a new, unique philosophical article. "
        f"CRITICAL RULE: You MUST NOT write about any of these previously covered topics:\n{history_text}\n\n"
        f"Choose a completely new topic or story. "
        f"Please return your response EXACTLY in this JSON format:\n"
        f"{{\n"
        f"  \"title\": \"A catchy, wise title for the article\",\n"
        f"  \"topic_summary\": \"A 1-sentence summary of the topic (to add to our history file)\",\n"
        f"  \"article_body\": \"The full markdown body of the article\"\n"
        f"}}"
    )

    print("🤖 Generating Spiritual/Philosophical article via Gemini...")
    if dry_run:
        result = {
            "title": "Dry Run Spiritual Tale",
            "topic_summary": "Dry run test topic",
            "article_body": "This is a dry run story."
        }
    else:
        result = generate_json("SpiritualCrunch", system_instruction, user_prompt, temperature=0.7)

    title = result.get("title", "Wisdom of the Ancients")
    slug = f"spiritual-wisdom-{datetime.datetime.now().strftime('%Y-%m-%d')}"
    
    # Save to history
    if not dry_run:
        history.append(result.get("topic_summary", title))
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

    # Generate Image
    print("🎨 Generating cover image...")
    image_prompt = f"Beautiful ethereal artwork representing {title}. Mystical, philosophical, clean vector illustration, soft lighting, no text."
    
    if dry_run:
        image_data = {
            "image_path": "/assets/images/posts/default-cover.png",
            "abs_path": None,
            "alt_text": f"Cover image for {title}",
            "generated": False,
        }
    else:
        abs_path = os.path.join(PROJECT_ROOT, "assets", "images", "posts", f"{slug}-cover.png")
        rel_path = f"/assets/images/posts/{slug}-cover.png"
        res_path = generate_cover_image(image_prompt, abs_path)
        
        image_data = {
            "image_path": rel_path if res_path else "/assets/images/posts/default-cover.png",
            "abs_path": abs_path if res_path else None,
            "alt_text": f"Cover image for {title}",
            "generated": bool(res_path),
        }

    seo_data = {
        "slug": slug,
        "excerpt": "A daily moment of philosophy and spiritual wisdom applied to modern life.",
        "category": "Geopolitics", # Reusing existing category to avoid Jekyll issues
        "tags": ["philosophy", "spiritual", "wisdom"]
    }

    markdown = generate_markdown(title, result.get("article_body", ""), seo_data, image_data)
    
    _save_article(markdown, slug, dry_run)


def _save_article(markdown: str, slug: str, dry_run: bool):
    filename = get_filename(slug)
    
    if dry_run:
        dry_run_dir = os.path.join(PROJECT_ROOT, "_dry_run_artifacts")
        os.makedirs(dry_run_dir, exist_ok=True)
        out_path = os.path.join(dry_run_dir, filename)
    else:
        out_path = os.path.join(PROJECT_ROOT, "_posts", filename)
        
    with open(out_path, "w") as f:
        f.write(markdown)
    
    print(f"✅ Saved article to {out_path}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mantbyte Daily Crunch Pipeline")
    parser.add_argument("--mode", required=True, choices=["world", "india", "finance", "spiritual"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Validate env
    if not os.environ.get("GEMINI_API_KEY") and not args.dry_run:
        print("❌ CRITICAL ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)

    print(f"🚀 Starting Daily Crunch Pipeline (Mode: {args.mode})")
    try:
        if args.mode in ["world", "india", "finance"]:
            run_news_crunch(args.mode, args.dry_run)
        elif args.mode == "spiritual":
            run_spiritual_crunch(args.dry_run)
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
