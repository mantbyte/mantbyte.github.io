"""
Agent 8: Image Generator
Generates cover images using Pollinations.ai.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_client import generate_cover_image, create_image_prompt


def generate_article_image(
    image_spec: dict,
    slug: str,
    repo_root: str = None,
) -> dict:
    """
    Generate a cover image for the article.
    
    Args:
        image_spec: Structured JSON specification from the Image Planner
        slug: URL-friendly slug
        repo_root: Path to repository root
    
    Returns:
        Dict with image_path (relative) and alt_text
    """
    if repo_root is None:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Generate optimized prompt from structured JSON
    prompt = create_image_prompt(image_spec)

    # Output path
    filename = f"{slug}-cover.png"
    abs_path = os.path.join(repo_root, "assets", "images", "posts", filename)
    rel_path = f"/assets/images/posts/{filename}"

    # Generate image
    result_path = generate_cover_image(
        prompt=prompt,
        output_path=abs_path,
        width=1200,
        height=630,
    )

    title = image_spec.get("main_subject", slug)
    if result_path:
        return {
            "image_path": rel_path,
            "abs_path": abs_path,
            "alt_text": f"Cover image for {title}",
            "generated": True,
        }
    else:
        print(f"  ⚠️ Using default cover image")
        return {
            "image_path": "/assets/images/posts/default-cover.png",
            "abs_path": None,
            "alt_text": f"Cover image for {title}",
            "generated": False,
        }
