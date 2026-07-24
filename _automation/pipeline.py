"""
Mantbyte AI Editorial Pipeline — Main Orchestrator

This is the entry point that chains all agents together.
Run with: python _automation/pipeline.py [--dry-run]
"""

import sys
import os
import json
import argparse
import time
import shutil

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.rss_reader import fetch_feeds
from agents.trend_detector import detect_trends
from agents.researcher import research_topic
from agents.fact_checker import verify_research
from agents.knowledge_base import check_duplicate, load_knowledge
from agents.editorial_planner import create_editorial_plan
from agents.writer import write_article
from agents.seo_optimizer import optimize_seo
from agents.image_generator import generate_article_image
from agents.markdown_generator import generate_markdown, get_filename
from agents.reviewer import review_article
from agents.publisher import publish_article


def validate_environment():
    """Fail fast if the environment is misconfigured."""
    print("🔍 Validating environment...")
    
    if not os.environ.get("GEMINI_API_KEY"):
        print("❌ CRITICAL ERROR: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
        
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    if not os.path.exists(config_path):
        print(f"❌ CRITICAL ERROR: Config file not found at {config_path}")
        sys.exit(1)
        
    required_dirs = ["_posts", "assets/images/posts", "_data"]
    for d in required_dirs:
        path = os.path.join(PROJECT_ROOT, d)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"  📁 Created missing directory: {d}")
            
    print("✅ Environment valid.\n")


def load_config() -> dict:
    """Load pipeline configuration."""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "r") as f:
        return json.load(f)


def print_summary(status: str, title: str, start_time: float, metrics: dict):
    """Print a highly readable end-of-run summary block."""
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)
    
    print("\n" + "=" * 60)
    print("📊 END-OF-RUN SUMMARY")
    print("=" * 60)
    print(f"Pipeline Status:  {status}")
    print(f"Topic:            {title if title else 'None selected'}")
    print(f"Execution Time:   {mins}m {secs}s")
    print("-" * 60)
    print(f"Research:         {metrics.get('research', 'Skipped')}")
    print(f"Duplicate Check:  {metrics.get('duplicate', 'Skipped')}")
    print(f"Writer:           {metrics.get('writer', 'Skipped')}")
    print(f"Reviewer:         {metrics.get('reviewer', 'Skipped')}")
    print(f"Markdown:         {metrics.get('markdown', 'Skipped')}")
    print(f"PR/Publish:       {metrics.get('publish', 'Skipped')}")
    print("=" * 60 + "\n")


def run_pipeline(dry_run: bool = False):
    """Execute the full editorial pipeline."""
    start_time = time.time()
    metrics = {}
    
    print("=" * 60)
    print("🚀 MANTBYTE AI EDITORIAL PIPELINE")
    print("=" * 60)

    validate_environment()
    config = load_config()

    if dry_run:
        dry_run_dir = os.path.join(PROJECT_ROOT, "_dry_run_artifacts")
        os.makedirs(dry_run_dir, exist_ok=True)

    # ─────────────────────────────────────────────
    # Stage 1: Trend Detection
    # ─────────────────────────────────────────────
    print("📡 STAGE 1: Trend Detection")
    print("-" * 40)

    articles = fetch_feeds(config["rss_feeds"], max_age_hours=48)
    if not articles:
        print("  ❌ No articles found from RSS feeds. Exiting cleanly.")
        print_summary("SUCCESS (No Feeds)", "", start_time, metrics)
        return True # Successful exit (clean skip)

    try:
        trends = detect_trends(articles)
        candidates = trends.get("candidates", [])
        if not candidates:
            print("  ❌ No trending topics identified. Exiting cleanly.")
            print_summary("SUCCESS (No Trends)", "", start_time, metrics)
            return True # Successful exit (clean skip)
    except Exception as e:
        print(f"  ❌ FATAL ERROR during Trend Detection: {e}")
        print("  💡 This usually means your API Key hit a rate limit (429) or is invalid.")
        print_summary("FAILED (API Error)", "", start_time, metrics)
        return False

    # ─────────────────────────────────────────────
    # Try each candidate until one succeeds
    # ─────────────────────────────────────────────
    for candidate_idx, candidate in enumerate(candidates):
        topic_title = candidate.get('original_title', '')[:60]
        print(f"\n{'=' * 60}")
        print(f"📌 Processing candidate #{candidate_idx + 1}: {topic_title}")
        print(f"{'=' * 60}")

        try:
            # ─────────────────────────────────────
            # Stage 2: Research
            # ─────────────────────────────────────
            print("\n📚 STAGE 2: Research")
            print("-" * 40)
            research = research_topic(candidate)
            metrics['research'] = 'Passed'

            # ─────────────────────────────────────
            # Stage 3: Fact Verification
            # ─────────────────────────────────────
            print("\n✅ STAGE 3: Source Verification")
            print("-" * 40)
            verification = verify_research(research)

            if not verification.get("verification_passed", False):
                confidence = verification.get("overall_confidence", "low")
                if confidence == "low":
                    print(f"  ⚠️ Verification failed. Trying next candidate...")
                    metrics['research'] = 'Failed Verification'
                    continue

            # ─────────────────────────────────────
            # Stage 4: Knowledge Base Check
            # ─────────────────────────────────────
            print("\n🧠 STAGE 4: Knowledge Base Check")
            print("-" * 40)
            cleaned = verification.get("cleaned_research", {})
            key_concepts = cleaned.get("technical_details", {}).get("key_concepts", [])
            knowledge = load_knowledge()
            kb_result = check_duplicate(
                topic=cleaned.get("topic", candidate.get("original_title", "")),
                key_concepts=key_concepts,
                knowledge=knowledge,
            )

            if kb_result.get("is_duplicate", False):
                print(f"  ⚠️ Duplicate topic detected. Trying next candidate...")
                metrics['duplicate'] = 'Failed (Duplicate)'
                continue
            metrics['duplicate'] = 'Passed'

            # ─────────────────────────────────────
            # Stage 5: Editorial Planning
            # ─────────────────────────────────────
            print("\n📋 STAGE 5: Editorial Planning")
            print("-" * 40)
            plan = create_editorial_plan(verification, kb_result)

            # ─────────────────────────────────────
            # Stage 6: Technical Writing
            # ─────────────────────────────────────
            print("\n✍️ STAGE 6: Technical Writing")
            print("-" * 40)
            article_body = write_article(plan, verification)

            if len(article_body.split()) < 800:
                print(f"  ⚠️ Article too short ({len(article_body.split())} words). Trying next candidate...")
                metrics['writer'] = 'Failed (Too Short)'
                continue
            metrics['writer'] = 'Passed'

            # ─────────────────────────────────────
            # Stage 7: SEO Optimization
            # ─────────────────────────────────────
            print("\n🔎 STAGE 7: SEO Optimization")
            print("-" * 40)
            seo = optimize_seo(
                title=plan.get("title", candidate.get("original_title", "")),
                article_body=article_body,
                category=candidate.get("category", "Tech"),
            )

            # ─────────────────────────────────────
            # Stage 8: Image Generation
            # ─────────────────────────────────────
            print("\n🎨 STAGE 8: Image Generation")
            print("-" * 40)

            if dry_run:
                image_data = {
                    "image_path": "/assets/images/posts/default-cover.png",
                    "abs_path": None,
                    "alt_text": f"Cover image for {plan.get('title', '')}",
                    "generated": False,
                }
                print("  ⏭️ Skipping image generation (dry run)")
            else:
                image_data = generate_article_image(
                    title=plan.get("title", ""),
                    slug=seo.get("slug", "article"),
                    category=seo.get("category", "Tech"),
                    key_concepts=key_concepts,
                    repo_root=PROJECT_ROOT,
                )

            # ─────────────────────────────────────
            # Stage 9: Markdown Assembly
            # ─────────────────────────────────────
            print("\n📝 STAGE 9: Markdown Generation")
            print("-" * 40)
            markdown = generate_markdown(
                title=plan.get("title", candidate.get("original_title", "")),
                article_body=article_body,
                seo_data=seo,
                image_data=image_data,
            )
            metrics['markdown'] = 'Valid'
            filename = get_filename(seo.get("slug", "article"))

            # ─────────────────────────────────────
            # Stage 10: Quality Review
            # ─────────────────────────────────────
            print("\n🔬 STAGE 10: Editorial Review")
            print("-" * 40)
            review = review_article(markdown, min_score=config["pipeline"]["min_quality_score"])
            
            score = review.get('score', 0)
            metrics['reviewer'] = f"{score}/10"

            if review.get("decision") == "FAIL":
                print(f"  ⚠️ Article failed quality review (score: {score}). Trying next candidate...")
                metrics['reviewer'] = f"{score}/10 (Failed)"
                continue

            # ─────────────────────────────────────
            # Stage 11: Publish (Write to disk)
            # ─────────────────────────────────────
            print("\n🚀 STAGE 11: Publishing")
            print("-" * 40)

            if dry_run:
                print(f"  ⏭️ DRY RUN — saving artifacts instead of modifying repository.")
                dry_run_file = os.path.join(dry_run_dir, filename)
                with open(dry_run_file, "w") as f:
                    f.write(markdown)
                print(f"  💾 Saved to: _dry_run_artifacts/{filename}")
                metrics['publish'] = 'Saved to Artifacts'
                print_summary("SUCCESS (DRY RUN)", plan.get('title', ''), start_time, metrics)
                return True

            pub_result = publish_article(
                markdown_content=markdown,
                filename=filename,
                seo_data=seo,
                editorial_plan=plan,
                image_data=image_data,
                review_result=review,
                repo_root=PROJECT_ROOT,
            )
            metrics['publish'] = 'Created'

            print_summary("SUCCESS", plan.get('title', ''), start_time, metrics)
            return True

        except Exception as e:
            print(f"  ❌ Error processing candidate: {e}")
            import traceback
            traceback.print_exc()
            metrics['publish'] = 'Error'
            continue

    # All candidates exhausted (Clean Skip)
    print_summary("SUCCESS (Skipped All Candidates)", "", start_time, metrics)
    return True # Return true so the GitHub Action doesn't fail, but no PR is created


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mantbyte AI Editorial Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Run without writing files or generating images")
    args = parser.parse_args()

    success = run_pipeline(dry_run=args.dry_run)
    sys.exit(0 if success else 1)
