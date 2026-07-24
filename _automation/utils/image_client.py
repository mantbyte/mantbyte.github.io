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


def create_image_prompt(image_spec: dict) -> str:
    """
    Create an optimized image generation prompt from a structured image specification.
    
    Args:
        image_spec: Structured JSON output from the Image Planner agent
    
    Returns:
        Optimized prompt string for image generation
    """
    
    main_subject = image_spec.get("main_subject", "Abstract technical illustration")
    scene_type = image_spec.get("scene_type", "editorial illustration")
    style = image_spec.get("visual_style", "clean vector illustration")
    camera = image_spec.get("camera_angle", "flat")
    lighting = image_spec.get("lighting", "soft lighting")
    colors = image_spec.get("color_palette", "professional colors")
    
    # Construct descriptive prompt
    prompt = f"A {style} of {main_subject}. Scene type: {scene_type}. Camera angle: {camera}. Lighting: {lighting}. Color palette: {colors}."
    
    # Add key objects
    objects = image_spec.get("key_objects", [])
    if objects:
        prompt += f" Must include: {', '.join(objects)}."
        
    # Add relationships/actions
    relationships = image_spec.get("relationships", [])
    if relationships:
        prompt += f" Details: {', '.join(relationships)}."
        
    # Add negative prompting via the "no [term]" pollinations convention
    avoid = image_spec.get("must_not_include", [])
    if avoid:
        prompt += f" no {', no '.join(avoid)}."
        
    # Hardcode core negative prompts to block tropes regardless of planner
    prompt += " no text, no words, no letters, no logos, no watermarks, no generic AI brains, no cyberpunk motherboards."

    return prompt
