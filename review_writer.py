"""REVIEW.md checklist writer with dedup and archiving."""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from scoring import severity_label

INTEL_DIR = Path("output/openclaw_intel")
REVIEW_PATH = INTEL_DIR / "REVIEW.md"
ARCHIVE_PATH = INTEL_DIR / "REVIEW_ARCHIVE.md"
SEEN_PATH = INTEL_DIR / "seen.json"


def load_seen() -> dict:
    """Load seen.json — returns {post_id: {score, first_seen}}."""
    if not SEEN_PATH.exists():
        return {}
    with open(SEEN_PATH, "r") as f:
        return json.load(f)


def save_seen(seen: dict) -> None:
    """Write seen dict to seen.json. Creates INTEL_DIR if needed."""
    INTEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(SEEN_PATH, "w") as f:
        json.dump(seen, f, indent=2)


def filter_new_items(df: pd.DataFrame, seen: dict) -> tuple:
    """Filter DataFrame to new or trending posts.

    Returns (filtered_df, updated_seen). Only processes posts, not comments.
    New posts are added to seen. Posts with score change >15 are flagged trending.
    """
    now = datetime.utcnow().isoformat()
    posts = df[df.get("type", pd.Series(["post"] * len(df))) != "comment"].copy()

    keep_indices = []
    posts["trending"] = False

    for idx, row in posts.iterrows():
        post_id = str(row.get("id", row.get("post_id", idx)))
        score = int(row.get("priority_score", row.get("score", 0)))

        if post_id not in seen:
            seen[post_id] = {"score": score, "first_seen": now}
            keep_indices.append(idx)
        else:
            prev_score = seen[post_id].get("score", 0)
            if abs(score - prev_score) > 15:
                posts.at[idx, "trending"] = True
                seen[post_id]["score"] = score
                keep_indices.append(idx)

    filtered = posts.loc[keep_indices].copy() if keep_indices else posts.iloc[0:0].copy()
    return filtered, seen


def _extract_pending_items(content: str) -> list:
    """Parse pending items from REVIEW.md content.

    Returns list of dicts with: score, title, stream, subreddit, posted,
    summary, link, checked, trending, raw_block.
    """
    pending_section = re.search(
        r"## Pending Review.*?\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if not pending_section:
        return []

    items = []
    blocks = re.split(r"\n(?=### \[)", pending_section.group(1))

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        header = re.match(
            r"### \[(\d+)\]\s*(TRENDING\s*—\s*)?(CRITICAL|HIGH|MEDIUM|LOW)\s*—\s*(.+)",
            block,
        )
        if not header:
            continue

        score = int(header.group(1))
        trending = bool(header.group(2))
        title = header.group(4).strip()

        stream_match = re.search(r"\*\*Stream:\*\*\s*([^|]+)", block)
        source_match = re.search(r"\*\*Source:\*\*\s*r/(\S+)", block)
        posted_match = re.search(r"\*\*Posted:\*\*\s*(\S+)", block)
        summary_match = re.search(r"\*\*Summary:\*\*\s*(.+)", block)
        link_match = re.search(r"\*\*Link:\*\*\s*(\S+)", block)
        checked = bool(re.search(r"\[x\]\s*Reviewed", block, re.IGNORECASE))

        items.append({
            "score": score,
            "title": title,
            "stream": stream_match.group(1).strip() if stream_match else "",
            "subreddit": source_match.group(1).strip() if source_match else "",
            "posted": posted_match.group(1).strip() if posted_match else "",
            "summary": summary_match.group(1).strip() if summary_match else "",
            "link": link_match.group(1).strip() if link_match else "",
            "checked": checked,
            "trending": trending,
        })

    return items


def _extract_reviewed_items(content: str) -> list:
    """Parse reviewed items from REVIEW.md.

    Returns list of dicts with: score, title, reviewed_date, raw_line.
    """
    reviewed_section = re.search(
        r"## Reviewed\s*\n(.*?)(?=\n## |\Z)", content, re.DOTALL
    )
    if not reviewed_section:
        return []

    items = []
    for match in re.finditer(
        r"### \[(\d+)\]\s*~~(.+?)~~\s*—\s*reviewed\s+(\S+)",
        reviewed_section.group(1),
    ):
        items.append({
            "score": int(match.group(1)),
            "title": match.group(2).strip(),
            "reviewed_date": match.group(3).strip(),
        })

    return items


def _format_pending_item(item: dict) -> str:
    """Format a single pending item as markdown."""
    trending_flag = "TRENDING — " if item.get("trending") else ""
    label = item.get("label", severity_label(item["score"]))
    title = item["title"][:100]

    lines = [
        f"### [{item['score']}] {trending_flag}{label} — {title}",
        f"- **Stream:** {item['stream']} | **Source:** r/{item['subreddit']} | **Posted:** {item['posted']}",
        f"- **Summary:** {item['summary'][:200]}",
        f"- **Link:** {item['link']}",
        "- [ ] Reviewed",
    ]
    return "\n".join(lines)


def _format_reviewed_item(item: dict) -> str:
    """Format a single reviewed item as markdown."""
    return f"### [{item['score']}] ~~{item['title']}~~ — reviewed {item['reviewed_date']}"


def update_review_md(new_items_df: pd.DataFrame, stream_label: str, max_new: int = 0) -> int:
    """Update REVIEW.md with new items, handle checked items, archive old ones.

    Args:
        new_items_df: DataFrame of new items to add.
        stream_label: Label for the stream these items came from.
        max_new: Max new items to add from this stream (0 = unlimited).

    Returns:
        Count of new items added.
    """
    INTEL_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.utcnow().strftime("%Y-%m-%d")
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M GMT")

    # Read existing REVIEW.md
    existing_content = ""
    if REVIEW_PATH.exists():
        existing_content = REVIEW_PATH.read_text()

    # Parse existing items
    pending_items = _extract_pending_items(existing_content)
    reviewed_items = _extract_reviewed_items(existing_content)

    # Move checked pending items to reviewed
    still_pending = []
    for item in pending_items:
        if item.get("checked"):
            reviewed_items.append({
                "score": item["score"],
                "title": item["title"],
                "reviewed_date": today,
            })
        else:
            still_pending.append(item)

    # Add new items from DataFrame (sorted by score, capped by max_new)
    new_count = 0
    rows = list(new_items_df.iterrows())
    rows.sort(key=lambda x: int(x[1].get("priority_score", x[1].get("score", 0))), reverse=True)
    for _, row in rows:
        score = int(row.get("priority_score", row.get("score", 0)))
        title = str(row.get("title", "Untitled"))[:100]
        text = str(row.get("text", row.get("body", "")))
        summary = text.replace("\n", " ").replace("\r", " ")[:200]
        posted = str(row.get("created_date", today))
        subreddit = str(row.get("subreddit", "unknown"))
        link = str(row.get("url", ""))
        trending = bool(row.get("trending", False))

        if max_new > 0 and new_count >= max_new:
            break

        still_pending.append({
            "score": score,
            "label": severity_label(score),
            "title": title,
            "stream": stream_label,
            "subreddit": subreddit,
            "posted": posted,
            "summary": summary,
            "link": link,
            "trending": trending,
        })
        new_count += 1

    # Sort pending by score descending
    still_pending.sort(key=lambda x: x["score"], reverse=True)

    # Archive reviewed items older than 30 days
    cutoff = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
    to_archive = [r for r in reviewed_items if r["reviewed_date"] < cutoff]
    reviewed_items = [r for r in reviewed_items if r["reviewed_date"] >= cutoff]

    if to_archive:
        archive_lines = []
        if ARCHIVE_PATH.exists():
            archive_lines.append(ARCHIVE_PATH.read_text().rstrip())
        else:
            archive_lines.append("# OpenClaw Intelligence — Review Archive\n")
        archive_lines.append(f"\n## Archived {today}\n")
        for item in to_archive:
            archive_lines.append(_format_reviewed_item(item))
        ARCHIVE_PATH.write_text("\n".join(archive_lines) + "\n")

    # Build REVIEW.md
    lines = [
        "# OpenClaw Intelligence Review",
        "",
        f"Last updated: {now_str}",
        "",
        "## Pending Review (sorted by priority)",
        "",
    ]

    if still_pending:
        for item in still_pending:
            lines.append(_format_pending_item(item))
            lines.append("")
    else:
        lines.append("*No pending items.*")
        lines.append("")

    lines.append("## Reviewed")
    lines.append("")

    if reviewed_items:
        for item in reviewed_items:
            lines.append(_format_reviewed_item(item))
    else:
        lines.append("*No reviewed items yet.*")

    lines.append("")
    REVIEW_PATH.write_text("\n".join(lines))

    return new_count
