"""OpenClaw scheduled scan orchestrator.

Runs both scan configs (use cases + security), scores results, deduplicates,
updates REVIEW.md, and prints an email digest.

Usage:
    python3 scheduled_scan.py
"""

import json
import re
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd

from email_digest import format_digest
from reddit_research import run_config
from review_writer import (
    INTEL_DIR,
    REVIEW_PATH,
    filter_new_items,
    load_seen,
    save_seen,
    update_review_md,
)
from scoring import score_items

SCAN_DIR = Path("scan_configs")
DIGEST_PATH = INTEL_DIR / "latest_digest.txt"


def _load_config(filename: str) -> dict:
    path = SCAN_DIR / filename
    with open(path, "r") as f:
        return json.load(f)


def _collect_digest_items(df: pd.DataFrame) -> list:
    """Extract digest-ready dicts from a scored DataFrame of new items."""
    items = []
    posts = df[df.get("type", pd.Series(["post"] * len(df))) != "comment"]
    for _, row in posts.iterrows():
        items.append({
            "score": int(row.get("priority_score", 0)),
            "title": str(row.get("title", "Untitled"))[:100],
            "subreddit": str(row.get("subreddit", "unknown")),
        })
    items.sort(key=lambda x: x["score"], reverse=True)
    return items


def _count_pending() -> int:
    """Count unchecked '- [ ] Reviewed' lines in REVIEW.md."""
    if not REVIEW_PATH.exists():
        return 0
    content = REVIEW_PATH.read_text()
    return len(re.findall(r"- \[ \] Reviewed", content))


def _oldest_unreviewed_days(seen: dict) -> int:
    """Estimate days since the oldest unreviewed item was first seen."""
    if not seen:
        return 0

    # Check which IDs are still pending in REVIEW.md
    # Approximate: oldest first_seen across all seen items
    oldest = None
    for entry in seen.values():
        first_seen = entry.get("first_seen")
        if not first_seen:
            continue
        try:
            dt = datetime.fromisoformat(first_seen)
        except (ValueError, TypeError):
            continue
        if oldest is None or dt < oldest:
            oldest = dt

    if oldest is None:
        return 0
    return max((datetime.utcnow() - oldest).days, 0)


def run_scan():
    """Run the full scan pipeline for both streams."""
    print("=" * 60)
    print("  OpenClaw Intelligence Scanner")
    print("=" * 60)
    print()

    seen = load_seen()
    usecases_digest_items = []
    security_digest_items = []

    # --- Stream 1: Use Cases ---
    print("[1/2] Use Cases stream")
    try:
        config = _load_config("openclaw_usecases.json")
        df, _analysis = run_config(config)
        print(f"      Scraped {len(df)} items from Reddit")

        df = score_items(df, stream="usecases")
        new_df, seen = filter_new_items(df, seen)
        added = update_review_md(new_df, "Use Cases")
        usecases_digest_items = _collect_digest_items(new_df)

        print(f"      {added} new items added to REVIEW.md")
    except Exception:
        print("      ERROR in Use Cases stream:")
        traceback.print_exc()
        print()

    # --- Stream 2: Security ---
    print("[2/2] Security stream")
    try:
        config = _load_config("openclaw_security.json")
        df, _analysis = run_config(config)
        print(f"      Scraped {len(df)} items from Reddit")

        df = score_items(df, stream="security")
        new_df, seen = filter_new_items(df, seen)
        added = update_review_md(new_df, "Security")
        security_digest_items = _collect_digest_items(new_df)

        print(f"      {added} new items added to REVIEW.md")
    except Exception:
        print("      ERROR in Security stream:")
        traceback.print_exc()
        print()

    # --- Save state ---
    save_seen(seen)

    # --- Build digest ---
    pending_count = _count_pending()
    oldest_days = _oldest_unreviewed_days(seen)

    subject, body = format_digest(
        usecases_digest_items,
        security_digest_items,
        pending_count,
        oldest_days,
    )

    print()
    print("-" * 60)
    print(f"Subject: {subject}")
    print("-" * 60)
    print(body)
    print("-" * 60)

    # Write digest to file
    INTEL_DIR.mkdir(parents=True, exist_ok=True)
    DIGEST_PATH.write_text(f"Subject: {subject}\n\n{body}\n")

    print()
    print("Output files:")
    print(f"  Review checklist: {REVIEW_PATH}")
    print(f"  Email digest:     {DIGEST_PATH}")
    print()


if __name__ == "__main__":
    run_scan()
