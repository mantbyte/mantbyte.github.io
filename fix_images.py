import os
import re
import urllib.parse
import urllib.request
import time
import ssl

POSTS_DIR = "_posts"
IMG_DIR = "assets/images/posts"

files_to_fix = [
    "2026-08-05-texas-data-center-moratorium-ai-energy-crisis.md",
    "2026-08-05-spiritual-wisdom-2026-08-05.md",
    "2026-08-05-world-news-crunch-2026-08-05.md",
    "2026-08-05-finance-news-crunch-2026-08-05.md",
    "2026-08-05-india-news-crunch-2026-08-05.md",
    "2026-08-05-ai-cybercrime-surge-africa-interpol.md",
    "2026-08-05-self-host-private-ai-coding-assistant.md",
    "2026-08-05-munich-open-source-sabbatical-libexpat.md"
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def generate_image(prompt, output_path):
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=400&nologo=true"
    
    print(f"Fetching image for: {prompt}")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                if response.status == 200:
                    with open(output_path, "wb") as f:
                        f.write(response.read())
                    return True
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(2)
    return False

for filename in files_to_fix:
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Skipping {filename}, does not exist.")
        continue
        
    with open(filepath, "r") as f:
        content = f.read()
        
    # Check if it actually needs fixing
    if "default-cover.png" not in content:
        print(f"Skipping {filename}, already has a specific image.")
        continue
        
    # Extract title
    title_match = re.search(r"^title:\s*['\"]?(.*?)['\"]?$", content, re.MULTILINE)
    if not title_match:
        print(f"Could not find title in {filename}")
        continue
        
    title = title_match.group(1)
    # create prompt based on title
    if "Spiritual" in title or "Empty Boat" in title:
        prompt = f"Beautiful ethereal artwork representing {title}. Mystical, philosophical, clean vector illustration, soft lighting, no text."
    elif "Crunch" in title:
        prompt = f"Professional news abstract background representing {title}. Minimalist, newsroom aesthetic, dark mode colors, digital art, no text."
    else:
        prompt = f"Professional abstract technology background representing {title}. Cybersecurity, programming, glowing lines, dark mode, no text."
        
    # Define image name
    slug = filename[11:-3] # remove date and .md
    img_filename = f"{slug}-cover.png"
    img_path = os.path.join(IMG_DIR, img_filename)
    
    if generate_image(prompt, img_path):
        # Update markdown file
        new_content = content.replace("/assets/images/posts/default-cover.png", f"/assets/images/posts/{img_filename}")
        with open(filepath, "w") as f:
            f.write(new_content)
        print(f"Successfully updated {filename}")
    else:
        print(f"Failed to generate image for {filename}")
