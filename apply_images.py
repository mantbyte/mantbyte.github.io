import os
import shutil
import glob

POSTS_DIR = "_posts"
IMG_DIR = "assets/images/posts"
ARTIFACTS_DIR = "/Users/sujalpanchal/.gemini/antigravity-ide/brain/84ed3448-a4cb-44d7-84bb-c1ad2eda4fb5"

mappings = {
    "2026-08-05-spiritual-wisdom-2026-08-05.md": "spiritual_boat",
    "2026-08-05-world-news-crunch-2026-08-05.md": "world_news",
    "2026-08-05-india-news-crunch-2026-08-05.md": "india_news",
    "2026-08-05-finance-news-crunch-2026-08-05.md": "finance_news",
    "2026-08-05-ai-cybercrime-surge-africa-interpol.md": "africa_cybercrime",
    "2026-08-05-self-host-private-ai-coding-assistant.md": "ai_coding_assistant",
    "2026-08-05-texas-data-center-moratorium-ai-energy-crisis.md": "texas_data_center",
    "2026-08-05-munich-open-source-sabbatical-libexpat.md": "munich_opensource"
}

for filename, prefix in mappings.items():
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"File not found: {filename}")
        continue
        
    # find artifact image
    search_pattern = os.path.join(ARTIFACTS_DIR, f"{prefix}_*.png")
    matches = glob.glob(search_pattern)
    if not matches:
        print(f"No image found for {prefix}")
        continue
        
    source_img = matches[0]
    
    # destination image
    slug = filename[11:-3]
    dest_img_name = f"{slug}-cover.png"
    dest_img_path = os.path.join(IMG_DIR, dest_img_name)
    
    # copy image
    shutil.copy2(source_img, dest_img_path)
    print(f"Copied image to {dest_img_path}")
    
    # update markdown file
    with open(filepath, "r") as f:
        content = f.read()
        
    new_content = content.replace("/assets/images/posts/default-cover.png", f"/assets/images/posts/{dest_img_name}")
    
    with open(filepath, "w") as f:
        f.write(new_content)
    print(f"Updated {filename}")
