# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Research automation that scrapes Reddit, performs sentiment analysis and entity tracking, and exports results to Excel with markdown reports.

## Workflow

1. **Brief** - User describes what they want to research
2. **Config** - Claude generates JSON config with search terms, subreddits, entities
3. **Iterate** - Review and refine config together
4. **Run** - Execute research with `python3 reddit_research.py config.json`

## Running Research

```bash
python3 reddit_research.py config.json
```

Outputs go to `output/` folder:
- `research_{topic}_{timestamp}.xlsx` - Multi-sheet Excel
- `research_{topic}_{timestamp}.md` - Markdown report

## Configuration Schema

```json
{
  "topic": "Research topic name",

  "search_terms": ["term 1", "term 2"],
  "subreddits": ["subreddit1", "subreddit2"],

  "entities_to_track": ["Company A", "Product B"],

  "keywords_positive": ["great", "recommend"],
  "keywords_negative": ["avoid", "terrible"],

  "limits": {"posts": 50, "comments": 3},
  "include_all_reddit": true,
  "all_reddit_limit": 10
}
```

**Required:** `topic`
**Optional:** Everything else (will use defaults or skip source if empty)

## Example Configs

Configs are stored with their project data in `output/{project}/`:

| Project Folder | Config | Use Case |
|----------------|--------|----------|
| `output/moneybox/` | `config_moneybox.json` | Company research (Reddit-only, competitor analysis) |
| `output/hargreaves_lansdown/` | `config_example_financial.json` | Financial services |
| `output/smart_bulbs/` | `config.json` | Product research |
| `output/mmwave_sensors/` | `config_mmw_sensors.json` | Product research |
| `output/health_research/` | `config_les_reflux.json` | Health research |
| `output/misc/` | `config_example_roles.json` | Job/career research (example) |

## Environment Setup

Create `.env` with Reddit API credentials:
```
REDDIT_CLIENT_ID=xxx
REDDIT_CLIENT_SECRET=xxx
REDDIT_USER_AGENT=xxx
```

Get credentials at: https://www.reddit.com/prefs/apps (select "script" type)

## Dependencies

```bash
pip install praw pandas openpyxl python-dotenv requests beautifulsoup4
```

## Folder Structure

```
├── reddit_research.py          # Main research script
├── legacy/                     # Deprecated scripts
└── output/                     # Generated files (gitignored)
    ├── {project}/              # One folder per research project
    │   ├── config_*.json       # Project config
    │   ├── *.xlsx              # Raw data (Excel)
    │   └── *.md                # Reports
    └── misc/                   # Example configs, unnamed research
```

## Known Issues & Improvement Ideas

*Updated: 2026-01-24*

### Issues Found
- **No sentiment over time** - Report doesn't show how sentiment has changed over time (would need date-based analysis)
- **Long filenames** - Topic names get truncated awkwardly in output filenames

### Potential Improvements
- [x] Filter "Top Posts" to only show posts mentioning the main entity/topic
- [ ] Add time-series sentiment analysis (sentiment by month/quarter)
- [ ] Add product/feature gap analysis (extract common complaints/requests)
- [ ] Shorter, cleaner output filenames
- [ ] Add competitor comparison chart to markdown report
- [ ] Show sample negative posts for issue identification
