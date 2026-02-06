# Quick Reference Card

## Run Research

```bash
python3 reddit_research.py config.json
```

## Config Structure

```json
{
  "topic": "What you're researching",
  "search_terms": ["query 1", "query 2"],
  "subreddits": ["subreddit1", "subreddit2"],
  "entities_to_track": ["Company A", "Product B"],
  "keywords_positive": ["great", "recommend", "love"],
  "keywords_negative": ["avoid", "terrible", "waste"],
  "limits": {"posts": 25, "comments": 3},
  "include_all_reddit": true,
  "all_reddit_limit": 10
}
```

**Required:** `topic`, `search_terms`, `subreddits`
**Optional:** everything else (defaults provided)

See [CONFIG_GUIDE.md](../CONFIG_GUIDE.md) for full field explanations and examples.

## Output Files

| File | Contents |
|------|----------|
| `research_*.xlsx` | Multi-sheet Excel: Summary, Posts, Comments, Entity Analysis, Subreddit Stats, Top Posts, Positive Highlights |
| `research_*.md` | Markdown summary report |
| `research_output.json` | Machine-readable metadata |

## Excel Sheets at a Glance

| Sheet | What to look for |
|-------|------------------|
| Summary | High-level stats: post count, sentiment split, date range |
| Posts | All posts sorted by score -- browse the raw data |
| Comments | Top comments sorted by score |
| Entity Analysis | Mention counts and sentiment per entity -- good for competitor comparison |
| Subreddit Stats | Which communities are most active on your topic |
| Top Posts | Highest-scoring posts across all subreddits |
| Positive Highlights | Positive-sentiment posts with good scores -- useful for testimonials |

## Limits Guide

| Use case | posts | comments | Approx. time |
|----------|-------|----------|--------------|
| Quick test | 10 | 2 | 2-5 min |
| Standard research | 25 | 3 | 5-10 min |
| Deep research | 50 | 5 | 15-30 min |

Total entries ≈ (search_terms x subreddits x posts) + (posts x comments)

## First-Time Setup

1. Install dependencies: `pip3 install -r requirements.txt`
2. Get Reddit API keys at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) (select "script" type)
3. Copy `.env.example` to `.env` and fill in your credentials

Full walkthrough: [SETUP_GUIDE.md](SETUP_GUIDE.md)

## Tips

- Start with small limits (10-20 posts) to test your search terms before scaling up
- More specific search terms = better results (`"iPhone 15 battery life"` beats `"iPhone"`)
- Search Reddit manually first to check your terms return useful discussions
- Include competitors in `entities_to_track` for comparison data
- Use domain-specific sentiment keywords (e.g. `"buggy"`, `"reliable"` for tech products)
