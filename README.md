# Reddit Research Tool

!!!THIS ONLY WORKS IF YOU HAVE A REDDIT API KEY AND APP AND POLICY CHANGE MEANS HARD TO GET NOW!!!

Research automation that scrapes Reddit, performs sentiment analysis and entity tracking, and exports results to Excel spreadsheets and markdown reports. 

Give it a topic, some search terms, and a list of entities to track -- it searches across subreddits, collects posts and comments, classifies sentiment, and produces a multi-sheet Excel workbook with a summary report.

## Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Set up Reddit API credentials (see Setup below)
cp .env.example .env
# Edit .env with your credentials

# 3. Run with a config file
python3 reddit_research.py config.json
```

## How It Works

1. **Configure** -- Create a JSON config with your topic, search terms, target subreddits, and entities to track
2. **Scrape** -- The tool searches each subreddit for each search term, collecting posts and top comments via the Reddit API
3. **Analyse** -- Posts are classified by sentiment (positive/negative/neutral) using keyword matching, and entity mentions are counted
4. **Export** -- Results go to a multi-sheet Excel file and a markdown summary report

### Output Files

| File | Contents |
|------|----------|
| `research_{topic}_{timestamp}.xlsx` | Multi-sheet Excel: Summary, Posts, Comments, Entity Analysis, Subreddit Stats, Top Posts, Positive Highlights |
| `research_{topic}_{timestamp}.md` | Markdown report with sentiment overview, entity table, top subreddits, top posts |
| `research_output.json` | Machine-readable summary for programmatic use |

## Setup

### Reddit API Credentials

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click **"create another app..."**
3. Select **"script"** as the app type
4. Set redirect URI to `http://localhost:8080`
5. Click **"create app"**
6. Copy the **client ID** (string under "personal use script") and **secret**

### Environment File

Copy `.env.example` to `.env` and fill in your credentials:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ResearchTool/1.0 by YourRedditUsername
```

### Dependencies

```bash
pip3 install -r requirements.txt
```

Requires Python 3.8+. Packages: `praw`, `pandas`, `openpyxl`, `python-dotenv`, `requests`, `beautifulsoup4`.

## Configuration

Create a JSON config file for each research project. Only `topic`, `search_terms`, and `subreddits` are required.

```json
{
  "topic": "Note-taking apps comparison",
  "search_terms": [
    "Notion vs Obsidian",
    "best note taking app",
    "Notion review"
  ],
  "subreddits": ["productivity", "Notion", "ObsidianMD"],
  "entities_to_track": ["Notion", "Obsidian", "Roam", "Evernote"],
  "keywords_positive": ["love", "great", "recommend", "game changer"],
  "keywords_negative": ["hate", "slow", "buggy", "frustrating"],
  "limits": {"posts": 25, "comments": 3},
  "include_all_reddit": true,
  "all_reddit_limit": 10
}
```

### Config Fields

| Field | Required | Description |
|-------|----------|-------------|
| `topic` | Yes | Research topic name. Used in filenames and reports. |
| `search_terms` | Yes | Search queries to find relevant posts. |
| `subreddits` | Yes | Subreddits to search (without `r/` prefix). |
| `entities_to_track` | No | Companies, products, or terms to count mentions and track sentiment for. |
| `keywords_positive` | No | Words indicating positive sentiment. Defaults provided. |
| `keywords_negative` | No | Words indicating negative sentiment. Defaults provided. |
| `limits.posts` | No | Max posts per subreddit/search term combo. Default: `50`. |
| `limits.comments` | No | Max top-level comments per post. Default: `3`. |
| `include_all_reddit` | No | Also search r/all for your terms. Default: `true`. |
| `all_reddit_limit` | No | Max posts from r/all per term. Default: `10`. |

See [CONFIG_GUIDE.md](CONFIG_GUIDE.md) for detailed field explanations and example configs for different use cases (product research, company analysis, career topics).

An example config is included at [`config_tutorial_example.json`](config_tutorial_example.json).

## Usage with Claude Code

This tool is designed to work with [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Start Claude Code in the project folder, describe what you want to research, and it will generate a config, run the tool, and help you interpret results.

```bash
cd claude-reddit-researcher
claude
```

Then just describe your research in plain English:

> Research what UK personal finance Reddit users think about Moneybox compared to Vanguard and Nutmeg. Focus on fees, app experience, and customer service.

Claude generates a config → you review and tweak → Claude runs the research → output files appear in the current folder.

See the [Setup Guide](docs/SETUP_GUIDE.md#running-research-with-claude-code) for more example prompts.

## Project Structure

```
├── reddit_research.py              # Main research script
├── requirements.txt                # Python dependencies
├── .env.example                    # Template for API credentials
├── config_tutorial_example.json    # Example config (note-taking apps)
├── CONFIG_GUIDE.md                 # Detailed config field reference
├── CLAUDE.md                       # Claude Code instructions
└── docs/
    ├── SETUP_GUIDE.md              # Step-by-step setup walkthrough
    └── QUICK_REFERENCE.md          # One-page cheat sheet
```

## License

Private repository.
