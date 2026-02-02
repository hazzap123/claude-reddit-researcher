# Reddit Research Tool - Setup Guide

A step-by-step guide to get the research tool running on your machine.

---

## Prerequisites

- **Python 3.8+** - Check with `python3 --version`
- **pip** - Python package manager (comes with Python)
- **Terminal access** - Command line / Terminal app

---

## Step 1: Get the Code

Option A - Clone/download this repository

Option B - Copy these files to a folder:
- `run_research.py`
- `reddit_research.py` (optional, Reddit-only version)
- One of the example config files

---

## Step 2: Install Dependencies

Open Terminal, navigate to the folder, and run:

```bash
pip3 install -r requirements.txt
```

This installs:
- `praw` - Reddit API client
- `pandas` - Data analysis
- `openpyxl` - Excel export
- `beautifulsoup4` - Web scraping
- `python-dotenv` - Environment variables

**Alternative (manual installation):**
```bash
pip3 install praw pandas openpyxl python-dotenv requests beautifulsoup4
```

---

## Step 3: Create Reddit API Credentials

### 3.1 Log into Reddit
Go to [reddit.com](https://reddit.com) and log in (create an account if needed).

### 3.2 Go to App Preferences
Navigate to: **https://www.reddit.com/prefs/apps**

Or: Click your profile → Settings → Safety & Privacy → scroll to bottom → "Manage third-party app authorization"

### 3.3 Create an App
1. Scroll to bottom and click **"create another app..."** (or "are you a developer? create an app...")

2. Fill in the form:
   - **name**: `research-tool` (or anything you like)
   - **App type**: Select **"script"** (important!)
   - **description**: `Personal research tool` (optional)
   - **about url**: leave blank
   - **redirect uri**: `http://localhost:8080` (required but not used)

3. Click **"create app"**

### 3.4 Copy Your Credentials

After creating, you'll see your app listed. Find these two values:

```
research-tool
personal use script
─────────────────────────
CLIENT_ID        ← The string under "personal use script" (looks like: M8sLHz...)

secret           CLIENT_SECRET ← Click "edit" to reveal, or it shows as "secret"
```

**Client ID**: The ~14 character string directly under your app name
**Client Secret**: Listed as "secret" (click edit if hidden)

---

## Step 4: Create .env File

In your project folder, create a file called `.env` (note the dot at the start):

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ResearchTool/1.0 by YourRedditUsername
```

Replace the values with your actual credentials.

**Example:**
```
REDDIT_CLIENT_ID=M8sLHzwn9w44b5v
REDDIT_CLIENT_SECRET=6oF2BVH9ffkM20rmtS3HAx47CWAAhg
REDDIT_USER_AGENT=ResearchTool/1.0 by ProductPro123
```

### Creating the file

**Mac/Linux Terminal:**
```bash
touch .env
open -e .env  # Opens in TextEdit
```

**Or any text editor** - just make sure to:
- Name it exactly `.env` (with the dot)
- Save as plain text (not .txt, not rich text)

---

## Step 5: Test the Setup

Create a simple test config called `test_config.json`:

```json
{
  "topic": "test run",
  "search_terms": ["product management"],
  "subreddits": ["ProductManagement"],
  "entities_to_track": ["Jira", "Notion", "Linear"],
  "limits": {"posts": 10, "comments": 2}
}
```

Run it:
```bash
python3 reddit_research.py test_config.json
```

You should see:
```
============================================================
RESEARCH TOOL
============================================================

📋 Topic: test run
🔍 Search terms: 1
📍 Subreddits: 1
...
✓ Connected to Reddit API
...
```

---

## Step 6: Check Output

Look in the `output/` folder for:
- `research_test_run_YYYYMMDD_HHMMSS.xlsx` - Excel with multiple sheets
- `research_test_run_YYYYMMDD_HHMMSS.md` - Markdown summary

---

## Troubleshooting

### "No module named 'praw'"
Run the pip install command again, make sure you're using the right Python:
```bash
python3 -m pip install praw pandas openpyxl python-dotenv requests beautifulsoup4
```

### "Reddit API not configured"
- Check `.env` file exists in the same folder as the script
- Check there are no quotes around the values
- Check no trailing spaces

### "401 Unauthorized" or "403 Forbidden"
- Double-check client_id and client_secret are correct
- Make sure you selected "script" type when creating the app
- Try regenerating the secret in Reddit app settings

### ".env file not found" on Windows
Windows might hide the dot. Use:
```bash
notepad .env
```
And save directly.

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 reddit_research.py config.json` | Run Reddit research |
| `pip3 install -r requirements.txt` | Install dependencies |
| `claude` | Start Claude Code assistant |

---

## Security Notes

- Never commit `.env` to git (it's in `.gitignore`)
- Reddit API is read-only with "script" type - it can only read public posts
- Rate limited to ~60 requests/minute - the script handles this automatically
