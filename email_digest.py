"""Email digest formatter for OpenClaw intelligence reports."""

from datetime import date


def format_digest(usecases_items, security_items, pending_count, oldest_unreviewed_days):
    """Format an OpenClaw intelligence digest email.

    Args:
        usecases_items: list of dicts with keys score, title, subreddit
        security_items: list of dicts with keys score, title, subreddit
        pending_count: total pending items in REVIEW.md
        oldest_unreviewed_days: age of oldest unreviewed item

    Returns:
        (subject, body) tuple — plain text, no HTML/markdown.
    """
    today = date.today()
    date_str = today.strftime("%A %-d %b %Y")

    total_count = len(usecases_items) + len(security_items)

    subject = f"OpenClaw Intel \u2014 {date_str} \u2014 {total_count} new items"

    separator = "=" * 50

    sections = []

    if security_items:
        lines = [f"SECURITY ALERTS ({len(security_items)} new)"]
        for item in security_items[:10]:
            title = item["title"][:70]
            lines.append(f"  [{item['score']}] {title} \u2014 r/{item['subreddit']}")
        sections.append("\n".join(lines))

    if usecases_items:
        lines = [f"USE CASES ({len(usecases_items)} new)"]
        for item in usecases_items[:10]:
            title = item["title"][:70]
            lines.append(f"  [{item['score']}] {title} \u2014 r/{item['subreddit']}")
        sections.append("\n".join(lines))

    body_parts = [
        f"OpenClaw Intelligence Digest \u2014 {date_str}",
        separator,
        "",
    ]

    if sections:
        body_parts.append("\n\n".join(sections))
    else:
        body_parts.append("No new items since last scan.")

    body_parts.extend([
        "",
        separator,
        f"Pending review: {pending_count} items | Oldest unreviewed: {oldest_unreviewed_days} days",
        "Full checklist: output/openclaw_intel/REVIEW.md",
    ])

    body = "\n".join(body_parts)
    return subject, body


if __name__ == "__main__":
    # Smoke test
    subject, body = format_digest(
        [{"score": 78, "title": "Test use case", "subreddit": "openclaw"}],
        [{"score": 92, "title": "Test security", "subreddit": "netsec"}],
        12, 5,
    )
    assert "OpenClaw Intel" in subject
    assert "2 new items" in subject
    assert "SECURITY ALERTS" in body
    assert "USE CASES" in body
    assert "Pending review: 12" in body
    print("All assertions passed")
    print()
    print("Subject:", subject)
    print()
    print(body)
