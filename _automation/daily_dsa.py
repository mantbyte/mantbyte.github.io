"""
Mantbyte Daily DSA Pipeline

Generates a daily Data Structures and Algorithms problem, complete with description, 
examples, constraints, hints, and optimal C++ solution.
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

from _ai.provider import generate_json
from utils.image_client import generate_cover_image
from agents.markdown_generator import generate_markdown, get_filename

def run_daily_dsa(dry_run: bool):
    """Generate a daily DSA problem."""
    history_file = os.path.join(PROJECT_ROOT, "_data", "dsa_history.json")
    
    # Ensure _data directory exists
    os.makedirs(os.path.dirname(history_file), exist_ok=True)
    
    try:
        with open(history_file, "r") as f:
            history = json.load(f)
    except Exception:
        history = []

    history_text = "\n".join([f"- {h}" for h in history[-50:]]) # Only send last 50 to save context
    
    system_instruction = (
        "You are an expert software engineer and competitive programming coach. "
        "Your task is to generate a 'Daily DSA Problem' for users to practice. "
        "The problem should be LeetCode-style (Easy, Medium, or Hard) and cover topics like "
        "Arrays, Strings, Linked Lists, Trees, Graphs, Dynamic Programming, or Sliding Window. "
        "Provide a clear problem description, 2-3 examples with explanations, constraints, "
        "an approach/hint section, and finally the optimal C++ solution with time/space complexity analysis."
    )
    
    user_prompt = (
        f"Please generate a new, unique DSA problem. "
        f"CRITICAL RULE: You MUST NOT generate any of these previously covered problems:\n{history_text}\n\n"
        f"Please return your response EXACTLY in this JSON format:\n"
        f"{{\n"
        f"  \"title\": \"Problem Title (e.g. 'Two Sum' or 'Merge Intervals')\",\n"
        f"  \"topic_summary\": \"A short summary (e.g. 'Array - Two Pointers - Find pair with sum')\",\n"
        f"  \"difficulty\": \"Easy | Medium | Hard\",\n"
        f"  \"article_body\": \"The full markdown body of the problem, including the problem statement, examples, constraints, approach, and C++ code block.\"\n"
        f"}}"
    )

    print("🤖 Generating Daily DSA Problem via Gemini...")
    if dry_run:
        result = {
            "title": "Dry Run DSA Problem",
            "topic_summary": "Dry run test topic",
            "difficulty": "Medium",
            "article_body": "This is a dry run problem."
        }
    else:
        result = generate_json("DailyDSA", system_instruction, user_prompt, temperature=0.7)

    title = result.get("title", "Daily DSA Challenge")
    difficulty = result.get("difficulty", "Medium")
    full_title = f"Daily DSA: {title} ({difficulty})"
    
    # Normalize slug
    safe_title = "".join(c for c in title.lower() if c.isalnum() or c == ' ').replace(' ', '-')
    slug = f"daily-dsa-{safe_title}-{datetime.datetime.now().strftime('%Y-%m-%d')}"
    
    # Save to history
    if not dry_run:
        history.append(result.get("topic_summary", title))
        with open(history_file, "w") as f:
            json.dump(history, f, indent=2)

    # Generate Image
    print("🎨 Generating cover image...")
    image_prompt = f"Abstract technical illustration representing {result.get('topic_summary', 'algorithms')} for the problem '{title}', code, logic, matrix style, clean vector tech art, dark theme, no text."
    
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
        "excerpt": f"Sharpen your coding skills with today's {difficulty} DSA problem: {title}.",
        "category": "DSA", 
        "tags": ["dsa", "cpp", "algorithms", difficulty.lower()]
    }

    markdown = generate_markdown(full_title, result.get("article_body", ""), seo_data, image_data)
    
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
    
    print(f"✅ Saved Daily DSA article to {out_path}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mantbyte Daily DSA Pipeline")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Validate env
    if not os.environ.get("GEMINI_API_KEY") and not args.dry_run:
        print("❌ CRITICAL ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)

    print("🚀 Starting Daily DSA Pipeline")
    try:
        run_daily_dsa(args.dry_run)
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
