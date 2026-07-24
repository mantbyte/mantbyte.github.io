"""
Image Generation Client — uses Pollinations.ai (free, no API key).
Generates cover images for blog posts.
"""

import os
import requests
import urllib.parse


def generate_cover_image(
    prompt: str,
    output_path: str,
    width: int = 1200,
    height: int = 630,
) -> str:
    """
    Generate a cover image using Pollinations.ai.
    
    Args:
        prompt: Descriptive text for the image
        output_path: Full path to save the image (e.g., assets/images/posts/slug-cover.png)
        width: Image width in pixels
        height: Image height in pixels
    
    Returns:
        The output_path on success, or fallback path on failure
    """
    try:
        # Build Pollinations URL
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"

        print(f"  🎨 Generating image: {prompt[:60]}...")

        import time
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=120, stream=True)
                if response.status_code == 200:
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)

                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    file_size = os.path.getsize(output_path)
                    print(f"  ✅ Image saved: {output_path} ({file_size // 1024}KB)")
                    return output_path
                else:
                    if attempt < retries - 1:
                        sleep_time = 2 ** attempt
                        print(f"  ⚠️ Image generation failed: HTTP {response.status_code}. Retrying in {sleep_time}s...")
                        time.sleep(sleep_time)
                    else:
                        print(f"  ❌ Image generation failed after {retries} attempts: HTTP {response.status_code}")
                        return None
            except requests.RequestException as e:
                if attempt < retries - 1:
                    sleep_time = 2 ** attempt
                    print(f"  ⚠️ Image network error: {e}. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    print(f"  ❌ Image network error after {retries} attempts: {e}")
                    return None

    except Exception as e:
        print(f"  ⚠️ Unexpected image generation error: {e}")
        return None


def create_image_prompt(title: str, category: str, key_concepts: list = None) -> str:
    """
    Create an optimized image generation prompt from article metadata.
    
    Args:
        title: Article title
        category: Article category (Tech, News, Geopolitics)
        key_concepts: Optional list of key technical concepts
    
    Returns:
        Optimized prompt string for image generation
    """
    concepts_str = ""
    if key_concepts:
        concepts_str = f", featuring {', '.join(key_concepts[:3])}"

    style_map = {
        "Tech": "modern digital illustration, dark background with neon accents, circuit board patterns, futuristic tech aesthetic",
        "News": "professional news media style, clean design, bold typography, minimalist composition",
        "Geopolitics": "world map visualization, geopolitical illustration, diplomatic style, earth tones with accent colors",
    }

    style = style_map.get(category, style_map["Tech"])

    prompt = (
        f"Blog cover image for article titled '{title}'{concepts_str}. "
        f"Style: {style}. "
        f"Wide landscape format, no text overlay, high quality, editorial photography style."
    )

    return prompt
