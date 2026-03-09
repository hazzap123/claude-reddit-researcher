"""Priority scoring engine for OpenClaw intelligence items.

Scores Reddit posts on a 0-100 priority scale. Two streams supported:
- usecases: balanced weights across engagement, sentiment, code quality, security, recency
- security: heavily weighted toward severity
"""

import re
import time

import pandas as pd


# --- Weight profiles ---

_WEIGHTS = {
    "usecases": {
        "upvotes": 0.25,
        "sentiment": 0.20,
        "code_quality": 0.15,
        "security_severity": 0.125,
        "recency": 0.15,
    },
    "security": {
        "severity": 0.50,
        "upvotes": 0.20,
        "sentiment": 0.15,
        "recency": 0.15,
    },
}

# --- Security keyword tiers ---

_SECURITY_HIGH = [
    "critical", "rce", "zero-day", "remote code execution",
    "arbitrary code", "authentication bypass", "privilege escalation",
]
_SECURITY_MEDIUM = [
    "vulnerability", "exploit", "injection", "bypass", "leak",
    "disclosure", "unpatched", "cve-",
]
_SECURITY_LOW = [
    "minor", "edge case", "low severity", "informational", "theoretical",
]

# --- Code quality signals ---

_CODE_POSITIVE = [
    "try", "except", "error", "validate", "sanitize",
    "auth", "test", "assert", "logging", "import hashlib", "import hmac",
]
_CODE_NEGATIVE = [
    "eval(", "exec(", "shell=True", "nosec", "noqa",
    "TODO", "FIXME", "HACK", "password =", "secret =",
]

# --- Recency constants ---

_FULL_SCORE_HOURS = 48
_DECAY_HOURS = 720  # 30 days


def severity_label(score: float) -> str:
    """Map a priority score to a severity label."""
    if score >= 80:
        return "CRITICAL"
    if score >= 60:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def score_items(df: pd.DataFrame, stream: str = "usecases") -> pd.DataFrame:
    """Add a `priority_score` column (0-100) to the DataFrame.

    Only posts are scored; comments receive 0.
    """
    if stream not in _WEIGHTS:
        raise ValueError(f"Unknown stream: {stream}. Choose from {list(_WEIGHTS)}")

    max_upvotes = df["score"].max() if "score" in df.columns and len(df) > 0 else 1
    max_upvotes = max(max_upvotes, 1)  # avoid division by zero

    scorer = _score_usecases if stream == "usecases" else _score_security

    def _calc(row):
        if row.get("type") != "post":
            return 0.0
        text = str(row.get("title", "")) + " " + str(row.get("body", ""))
        return round(scorer(row, text, max_upvotes), 1)

    df["priority_score"] = df.apply(_calc, axis=1)
    return df


# --- Stream scorers ---


def _score_usecases(row, text: str, max_upvotes: float) -> float:
    w = _WEIGHTS["usecases"]
    upvotes = min(row.get("score", 0) / max_upvotes, 1.0) if max_upvotes else 0
    sentiment = _sentiment_score(row.get("sentiment"))
    code = _code_quality_score(text)
    security = _security_severity_score(text)
    recency = _recency_score(row.get("created_utc"))

    return (
        w["upvotes"] * upvotes
        + w["sentiment"] * sentiment
        + w["code_quality"] * code
        + w["security_severity"] * security
        + w["recency"] * recency
    ) * 100


def _score_security(row, text: str, max_upvotes: float) -> float:
    w = _WEIGHTS["security"]
    severity = _security_severity_score(text)
    upvotes = min(row.get("score", 0) / max_upvotes, 1.0) if max_upvotes else 0
    sentiment = _sentiment_score(row.get("sentiment"))
    recency = _recency_score(row.get("created_utc"))

    return (
        w["severity"] * severity
        + w["upvotes"] * upvotes
        + w["sentiment"] * sentiment
        + w["recency"] * recency
    ) * 100


# --- Component scorers ---


def _sentiment_score(sentiment) -> float:
    """Map sentiment label to 0-1 score."""
    mapping = {"Positive": 1.0, "Neutral": 0.5, "Negative": 0.0}
    return mapping.get(str(sentiment), 0.5)


def _security_severity_score(text: str) -> float:
    """Score text for security severity based on keyword matching."""
    lower = text.lower()
    for kw in _SECURITY_HIGH:
        if kw in lower:
            return 1.0
    for kw in _SECURITY_MEDIUM:
        if kw in lower:
            return 0.6
    for kw in _SECURITY_LOW:
        if kw in lower:
            return 0.2
    return 0.0


def _code_quality_score(text: str) -> float:
    """Score code quality from code blocks in text.

    Returns ratio of positive signals / (positive + negative).
    0.5 if no code blocks found.
    """
    code_blocks = re.findall(r"```[\s\S]*?```", text)
    if not code_blocks:
        return 0.5

    code_text = " ".join(code_blocks)
    positive = sum(1 for sig in _CODE_POSITIVE if sig in code_text)
    negative = sum(1 for sig in _CODE_NEGATIVE if sig in code_text)

    total = positive + negative
    if total == 0:
        return 0.5
    return positive / total


def _recency_score(created_utc) -> float:
    """Score recency: 1.0 within 48h, linear decay to 0 at 30 days."""
    if created_utc is None or pd.isna(created_utc):
        return 0.0

    age_hours = (time.time() - float(created_utc)) / 3600

    if age_hours <= _FULL_SCORE_HOURS:
        return 1.0
    if age_hours >= _DECAY_HOURS:
        return 0.0

    return 1.0 - (age_hours - _FULL_SCORE_HOURS) / (_DECAY_HOURS - _FULL_SCORE_HOURS)
