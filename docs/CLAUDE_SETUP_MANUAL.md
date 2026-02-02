# Customer Research Automation Tutorial

**Duration:** 60 minutes
**Format:** Hands-on tutorial
**Goal:** Set up and run your first AI-powered customer research

By the end of this tutorial, you'll have a working tool that turns a plain English research brief into structured customer intelligence from Reddit.

---

## What You'll Build

```
"I want to understand what customers think about [X]"
                    ↓
              Claude Code
                    ↓
           Structured research
          (sentiment, competitors,
           quotes, trends)
```

---

## Agenda

| Time | Section | What You'll Do |
|------|---------|----------------|
| 0-10 min | Setup: Claude Code | Install the AI coding assistant |
| 10-20 min | Setup: Python & Dependencies | Get the research scripts running |
| 20-35 min | Setup: Reddit API | Create app, get credentials |
| 35-50 min | Hands-on: Your First Research | Brief Claude, generate config, run it |
| 50-60 min | Explore & Next Steps | Customize, iterate, Q&A |

---

## Part 1: Install Claude Code (10 min)

Claude Code is a command-line AI assistant that can write code, run commands, and iterate with you on tasks.

### Step 1.1: Open Terminal

**Mac:** Press `Cmd + Space`, type "Terminal", hit Enter
**Windows:** Press `Win + R`, type "cmd", hit Enter (or use PowerShell)

### Step 1.2: Install Claude Code

Run this command:

```bash
npm install -g @anthropic-ai/claude-code
```

**Don't have npm?** Install Node.js first:
- Mac: `brew install node` (or download from nodejs.org)
- Windows: Download from https://nodejs.org

### Step 1.3: Authenticate

```bash
claude
```

This opens a browser window to sign in with your Anthropic account.
(If you don't have one, create it at https://console.anthropic.com)

### Step 1.4: Verify It Works

After signing in, you should see:

```
Welcome to Claude Code!
```

Type `exit` to leave for now - we'll come back to it.

**Checkpoint:** Claude Code installed and authenticated.

---

## Part 2: Python & Dependencies (10 min)

### Step 2.1: Check Python Version

```bash
python3 --version
```

You need **Python 3.8 or higher**. If you see an error or lower version:

**Mac:**
```bash
brew install python3
```

**Windows:**
Download from https://www.python.org/downloads/

### Step 2.2: Get the Research Tool

**Option A - Download ZIP:**
Download and unzip this package to a folder (e.g., `~/claude-researcher`)

**Option B - Clone with git:**
```bash
git clone [repository-url] claude-researcher
cd claude-researcher
```

### Step 2.3: Install Dependencies

Navigate to the folder and run:

```bash
cd ~/claude-researcher  # or wherever you put it
pip3 install -r requirements.txt
```

This installs:
- `praw` - Reddit API client
- `pandas` - Data analysis
- `openpyxl` - Excel export
- `beautifulsoup4` - Web scraping
- `python-dotenv` - Environment variables

**Checkpoint:** Python working, dependencies installed.

---

## Part 3: Reddit API Setup (15 min)

This is the most involved step - but you only do it once.

### Step 3.1: Log into Reddit

Go to https://reddit.com and log in (create a free account if needed).

### Step 3.2: Create a Reddit App

1. Go to: **https://www.reddit.com/prefs/apps**

2. Scroll to the bottom, click **"create another app..."**

3. Fill in the form:

| Field | Value |
|-------|-------|
| name | `research-tool` |
| App type | **script** (important!) |
| description | `Personal research tool` |
| about url | (leave blank) |
| redirect uri | `http://localhost:8080` |

4. Click **"create app"**

### Step 3.3: Copy Your Credentials

After creating, you'll see your app. Find these values:

```
research-tool
personal use script
─────────────────────────
abc123xyz     ← This is your CLIENT_ID (under the app name)

secret: def456...  ← This is your CLIENT_SECRET
```

**Write these down** - you'll need them in the next step.

### Step 3.4: Create the .env File

In your research-tool folder, create a file called `.env`:

```bash
touch .env
```

Open it in a text editor and add:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ResearchTool/1.0 by YourRedditUsername
```

Replace the placeholder values with your actual credentials.

**Example:**
```
REDDIT_CLIENT_ID=abc123xyz
REDDIT_CLIENT_SECRET=def456uvw789
REDDIT_USER_AGENT=ResearchTool/1.0 by productpro
```

### Step 3.5: Test the Connection

Run a quick test:

```bash
python3 -c "
from dotenv import load_dotenv
import praw
import os
load_dotenv()
reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
    client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
    user_agent=os.getenv('REDDIT_USER_AGENT')
)
print('Connected! Read-only:', reddit.read_only)
"
```

You should see: `Connected! Read-only: True`

**Checkpoint:** Reddit API working.

---

## Part 4: Your First Research (15 min)

Now the fun part - let's run actual research!

### Step 4.1: Start Claude Code in the Project

```bash
cd ~/claude-researcher  # your project folder
claude
```

### Step 4.2: Give Claude Your Research Brief

Type something like:

```
I want to research what people think about [YOUR TOPIC].
Help me create a config file and run the research.
```

**Example briefs:**
- "Research what people think about Notion vs Obsidian for note-taking"
- "Find out what UK personal finance users say about robo-advisors"
- "Understand sentiment around remote work tools in 2024"

### Step 4.3: Review the Config with Claude

Claude will generate a JSON config file. Review it together:

- **search_terms** - Are these the right queries?
- **subreddits** - Are these relevant communities?
- **entities_to_track** - Any competitors/products to add?
- **keywords_positive/negative** - Adjust for your domain

Ask Claude to modify anything that doesn't look right.

### Step 4.4: Run the Research

Once you're happy with the config, Claude will run:

```bash
python3 reddit_research.py your_config.json
```

Watch the output - you'll see it searching Reddit and collecting data.

### Step 4.5: Review Your Results

When complete, you'll have two files in `output/`:

1. **Excel file** (`.xlsx`) - Full data with multiple sheets:
   - Summary stats
   - All posts and comments
   - Entity analysis with sentiment
   - Top posts

2. **Markdown report** (`.md`) - Executive summary:
   - Sentiment breakdown
   - Entity comparison table
   - Top relevant posts

Open them and explore!

**Checkpoint:** First research complete!

---

## Part 5: Explore & Customize (10 min)

### Try Different Research

Ask Claude for a new research topic:

```
Now let's research [something else you're curious about]
```

### Understand the Config Options

```json
{
  "topic": "What the research is about",

  "search_terms": ["queries to search"],
  "subreddits": ["communities to search"],

  "entities_to_track": ["Companies", "Products", "Features"],

  "keywords_positive": ["great", "love", "recommend"],
  "keywords_negative": ["terrible", "avoid", "hate"],

  "limits": {"posts": 50, "comments": 3},
  "include_all_reddit": true,
  "all_reddit_limit": 10
}
```

### Tips for Better Research

1. **Be specific with search terms** - "Moneybox LISA review" beats "savings app"
2. **Choose relevant subreddits** - Look where your users actually hang out
3. **Track competitors** - The entity analysis shows relative sentiment
4. **Customize sentiment keywords** - Add domain-specific terms

---

## Troubleshooting

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### "Reddit API not configured"
Check your `.env` file exists and has no typos or extra spaces.

### "401 Unauthorized"
- Verify client_id and client_secret are correct
- Make sure you selected "script" type for your Reddit app
- Try regenerating the secret

### Research is slow
- Reduce `limits.posts` to get faster results
- Remove `include_all_reddit` for targeted research

---

## What's Next?

### Ideas for Research
- Competitor analysis
- Feature gap discovery
- Pricing sentiment
- Market validation
- Customer pain points

### Extend the Tool
- Add other data sources (MoneySavingExpert forums, Hacker News)
- Improve sentiment analysis with custom keywords
- Build a dashboard for tracking over time

### Share Your Findings
The markdown report is designed to share with stakeholders - just copy and paste.

---

## Quick Reference

| Command | What it does |
|---------|--------------|
| `claude` | Start Claude Code |
| `python3 reddit_research.py config.json` | Run research |
| `pip3 install -r requirements.txt` | Install dependencies |

| File | Purpose |
|------|---------|
| `.env` | Reddit API credentials (keep private!) |
| `config_*.json` | Research configuration |
| `reddit_research.py` | Research script |
| `output/*.xlsx` | Full data export |
| `output/*.md` | Summary report |

---

## Resources

- **SETUP_GUIDE.md** - Detailed setup instructions
- **CLAUDE.md** - Project overview and config reference
- **Example configs** - In `output/` subfolders

---

*Built with Claude Code - AI-powered customer research in minutes, not days.*
