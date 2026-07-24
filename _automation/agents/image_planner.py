"""
Agent 8: Image Planner
Acts as a Technical Art Director to plan semantically accurate image specifications.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from _ai.provider import generate_json


def plan_image(title: str, article_body: str, category: str, key_concepts: list, plan: dict = None) -> dict:
    """
    Plan the semantic image specification based on the article content.
    Includes a self-reflection gate to prevent generic "AI motherboard" tropes.
    """
    
    system_instruction = """You are the Technical Art Director for Mantbyte, an elite engineering and technology publication (similar to the Cloudflare Blog or Stripe Engineering).
Your job is to read an article and design a precise, semantic image specification for the cover illustration.

CRITICAL RULES:
1. NEVER use generic tropes like "glowing AI chips", "neon circuit boards", "futuristic processors", "cyberpunk motherboards", or "floating binary code".
2. If the article is about software (e.g., CORS, CI/CD, OAuth, Docker), the image MUST visualize the architecture, workflow, data flow, or system interaction (e.g., a diagram of a browser talking to a server, or containers deploying).
3. If the article is about AI architecture (e.g., LLM alignment, RLHF), visualize the concepts (e.g., safety layers, prompt pipelines, model training flow) NOT physical computer hardware.
4. Always prefer technical editorial illustrations, flat professional vectors, or clean isometric diagrams over hyper-realistic sci-fi artwork.
5. NO text overlays, logos, or watermarks in the image.

Output your specification strictly as a JSON object matching this schema:
{
  "main_subject": "Primary focus of the illustration",
  "secondary_subject": "Secondary elements to include",
  "key_objects": ["list", "of", "specific", "visual", "elements"],
  "relationships": ["How objects interact, e.g., 'A feeds into B'"],
  "scene_type": "e.g., architecture diagram, isometric system view, workflow illustration",
  "camera_angle": "e.g., top-down, isometric, flat, macro",
  "composition": "e.g., balanced, central focus, flow from left to right",
  "lighting": "e.g., clean studio lighting, soft flat lighting, high contrast",
  "color_palette": "e.g., professional blues and whites, dark mode with teal accents",
  "visual_style": "e.g., clean vector illustration, technical editorial style, flat design",
  "background": "e.g., solid dark blue, minimalist geometric patterns",
  "must_not_include": ["list", "of", "tropes", "to", "avoid", "like", "AI chips", "motherboards", "text", "binary"],
  "semantic_relevance": 0-100 (Score how well this illustrates the actual technical concept),
  "genericity_score": 0-10 (Score 10 if it relies on generic tech tropes like glowing chips/brains. Score 0 if it is a highly specific diagram),
  "concept_coverage": 0-100 (Score how well it covers the key entities),
  "explanation": "Brief explanation of why this visualization was chosen and how it avoids generic tropes."
}
"""

    # Summarize article body to save tokens if it's too long
    summary_body = article_body[:3000] + "\n...(truncated)" if len(article_body) > 3000 else article_body

    user_prompt = f"""
Please design an image specification for the following article:

Title: {title}
Category: {category}
Key Concepts / Entities: {', '.join(key_concepts) if key_concepts else 'None provided'}

Article Content:
{summary_body}
"""

    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"  🎨 Planning image (Attempt {attempt + 1}/{max_retries})...")
            spec = generate_json("image_planner", system_instruction, user_prompt, temperature=0.4 + (attempt * 0.2))
            
            # Self-reflection quality gate
            genericity = spec.get("genericity_score", 10)
            relevance = spec.get("semantic_relevance", 0)
            
            if genericity > 4:
                print(f"    ⚠️ Image plan rejected by quality gate (Genericity: {genericity}/10). Retrying...")
                # Append to prompt to aggressively steer away from what it just did
                user_prompt += f"\n\nPrevious attempt was rejected because it was too generic (Score: {genericity}/10). You MUST use a completely different, highly specific visualization strategy. NO HARDWARE. NO GLOWING CHIPS."
                continue
                
            if relevance < 70:
                print(f"    ⚠️ Image plan rejected by quality gate (Relevance: {relevance}/100). Retrying...")
                user_prompt += f"\n\nPrevious attempt was rejected because it lacked semantic relevance (Score: {relevance}/100). Ensure the image directly visualizes the core concepts of the article."
                continue
                
            print(f"    ✅ Image plan approved (Genericity: {genericity}/10, Relevance: {relevance}/100)")
            return spec
            
        except Exception as e:
            print(f"    ⚠️ Planner error: {e}")
            if attempt == max_retries - 1:
                break
                
    # Fallback spec if generation completely fails
    print("    ⚠️ Using fallback image specification due to repeated failures.")
    return {
        "main_subject": f"Abstract representation of {category}",
        "secondary_subject": ", ".join(key_concepts[:2]) if key_concepts else "",
        "key_objects": ["minimalist geometric shapes"],
        "relationships": [],
        "scene_type": "minimalist editorial illustration",
        "camera_angle": "flat",
        "composition": "central focus",
        "lighting": "soft lighting",
        "color_palette": "professional brand colors",
        "visual_style": "clean minimal vector illustration",
        "background": "solid dark background",
        "must_not_include": ["text", "logos", "watermarks", "AI processors", "glowing chips", "motherboards"],
        "semantic_relevance": 50,
        "genericity_score": 5,
        "concept_coverage": 50,
        "explanation": "Fallback generated due to planning failure."
    }

if __name__ == "__main__":
    # Test
    sample_body = "Cross-Origin Resource Sharing (CORS) is an HTTP-header based mechanism that allows a server to indicate any origins (domain, scheme, or port) other than its own from which a browser should permit loading resources."
    spec = plan_image("AI-Generated CORS Misconfigurations", sample_body, "Tech", ["CORS", "Browsers", "Security"])
    print(json.dumps(spec, indent=2))
