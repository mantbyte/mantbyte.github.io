"""Generate temporary distribution events from newly added Jekyll posts."""

import argparse
import json
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

import yaml


ZERO_SHA = "0" * 40
DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
FRONT_MATTER = re.compile(r"^---\s*\n(.*?)\n---\s*(?:\n|$)", re.DOTALL)


def _git_changed_posts(repo_root: Path, before: str, after: str) -> list[Path]:
    """Return newly added Markdown posts between two commits."""
    if not after:
        raise ValueError("The commit being deployed is required")

    if before and before != ZERO_SHA:
        command = [
            "git", "diff", "--name-only", "--diff-filter=A", before, after,
            "--", "_posts",
        ]
    else:
        command = [
            "git", "diff-tree", "--root", "--no-commit-id", "--name-only",
            "--diff-filter=A", "-r", after, "--", "_posts",
        ]

    result = subprocess.run(
        command,
        cwd=repo_root,
        check=True,
        capture_output=True,
        text=True,
    )

    paths = []
    for line in result.stdout.splitlines():
        path = Path(line.strip())
        if path.parts and path.parts[0] == "_posts" and path.suffix == ".md":
            paths.append(path)
    return paths


def _read_front_matter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError(f"{path} has no valid YAML front matter")

    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{path} front matter must be a mapping")
    return metadata, text[match.end():]


def _as_category(value) -> str:
    if isinstance(value, list):
        value = value[0] if value else "Tech"
    return str(value or "Tech")


def _as_iso_datetime(value) -> str:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc).isoformat()
    if value:
        return str(value)
    return datetime.now(timezone.utc).isoformat()


def _excerpt(metadata: dict, body: str) -> str:
    value = metadata.get("excerpt")
    if value:
        return str(value).strip()

    paragraph = re.sub(r"\s+", " ", body.strip()).strip()
    return paragraph[:280] + ("..." if len(paragraph) > 280 else "")


def _event_for_post(repo_root: Path, relative_path: Path) -> dict:
    path = repo_root / relative_path
    metadata, body = _read_front_matter(path)

    title = str(metadata.get("title", "")).strip()
    if not title:
        raise ValueError(f"{relative_path} is missing a title")

    category = _as_category(metadata.get("categories", metadata.get("category")))
    slug = str(metadata.get("slug") or DATE_PREFIX.sub("", path.stem))
    published_at = _as_iso_datetime(metadata.get("date"))
    url = metadata.get("url")
    if not url:
        parsed_date = metadata.get("date")
        if isinstance(parsed_date, (datetime, date)):
            date_path = f"{parsed_date.year:04d}/{parsed_date.month:02d}/{parsed_date.day:02d}"
        else:
            date_path = DATE_PREFIX.match(path.stem).group(0)[:-1].replace("-", "/") if DATE_PREFIX.match(path.stem) else ""
        url = f"/{category.lower()}/{date_path}/{slug}.html" if date_path else f"/{slug}.html"

    tags = metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    return {
        "event": "article_published",
        "title": title,
        "slug": slug,
        "category": category,
        "excerpt": _excerpt(metadata, body),
        "url": str(url),
        "cover_image": str(metadata.get("cover_image", "")),
        "tags": tags if isinstance(tags, list) else [],
        "published_at": published_at,
        "filename": path.name,
    }


def generate_events(repo_root: Path, before: str, after: str, output_dir: Path) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    posts = _git_changed_posts(repo_root, before, after)

    for index, post in enumerate(posts, start=1):
        event = _event_for_post(repo_root, post)
        output_path = output_dir / f"event-{index:04d}.json"
        output_path.write_text(json.dumps(event, indent=2) + "\n", encoding="utf-8")
        print(f"  📡 Generated event for {post}")

    print(f"Generated {len(posts)} distribution event(s).")
    return len(posts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", default="", help="Previous push commit SHA")
    parser.add_argument("--after", required=True, help="Commit SHA being deployed")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[2]
    generate_events(repo_root, args.before, args.after, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
