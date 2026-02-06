# Reddit Research Tool - Setup Guide

A step-by-step guide to get the research tool running on your machine.

---

## Prerequisites

- **Python 3.8+** -- Check by opening Terminal and typing `python3 --version`. If you don't have it, download from [python.org](https://www.python.org/downloads/).
- **A Reddit account** -- Needed to create API credentials (free).
- **Terminal / Command Line** -- On Mac, search for "Terminal" in Spotlight. On Windows, use Command Prompt or PowerShell.

---

## Step 1: Get the Code

**If you have git installed:**

```bash
git clone https://github.com/hazzap123/claude-reddit-researcher.git
cd claude-reddit-researcher
```

**If you don't have git:** Go to [github.com/hazzap123/claude-reddit-researcher](https://github.com/hazzap123/claude-reddit-researcher), click the green **"Code"** button, then **"Download ZIP"**. Extract the ZIP, then open a terminal and navigate to the folder:

```bash
cd ~/downloads/claude-reddit-researcher-main
```

All remaining commands should be run from inside the project folder.

---

## Step 2: Install Dependencies

```bash
pip3 install -r requirements.txt
```

This installs the Python packages the tool needs:
- `praw` -- Reddit API client
- `pandas` -- Data analysis
- `openpyxl` -- Excel export
- `beautifulsoup4` -- Web scraping
- `python-dotenv` -- Environment variables

If you get a "pip3 not found" error, try:
```bash
python3 -m pip install -r requirements.txt
```

---

## Step 3: Create Reddit API Credentials

### 3.1 Log into Reddit

Go to [reddit.com](https://reddit.com) and log in. If you don't have a Reddit account, create one first (it's free).

### 3.2 Go to App Preferences

Navigate to: **https://www.reddit.com/prefs/apps**

If that link doesn't work, you can get there manually: click your profile icon → Settings → Safety & Privacy → scroll to the bottom → "Manage third-party app authorization".

### 3.3 Create an App

1. Scroll to the bottom and click **"create another app..."** (or **"are you a developer? create an app..."**)

2. Fill in the form:
   - **name**: `research-tool` (or anything you like)
   - **App type**: Select **"script"** (important!)
   - **description**: leave blank
   - **about url**: leave blank
   - **redirect uri**: `http://localhost:8080`

3. Click **"create app"**

### 3.4 Find Your Credentials

After creating, you'll see your app listed on the page. You need two values:

- **Client ID** -- The short string (about 14 characters) shown directly under your app name and the words "personal use script". It looks something like `M8sLHzwn9w44b5v`.
- **Client Secret** -- Listed next to "secret". If it's hidden, click "edit" to reveal it.

Keep this page open -- you'll need these values in the next step.

---

## Step 4: Create .env File

A `.env.example` template is included in the repo. Copy it and fill in your credentials:

**Mac/Linux:**
```bash
cp .env.example .env
```

**Windows:**
```bash
copy .env.example .env
```

Then open `.env` in any text editor and replace the placeholder values with the credentials from Step 3:

```
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=ResearchTool/1.0 by YourRedditUsername
```

For `REDDIT_USER_AGENT`, replace `YourRedditUsername` with your actual Reddit username.

---

## Step 5: Test the Setup

An example config is included in the repo. Run it to check everything works:

```bash
python3 reddit_research.py config_tutorial_example.json
```

You should see output like:

```
============================================================
REDDIT RESEARCH TOOL
============================================================

📋 Topic: Note-taking apps comparison
🔍 Search terms: 5
📍 Subreddits: productivity, Notion, ObsidianMD
...
✓ Connected (read-only: True)
...
```

If you see "Connected" then your API credentials are working.

---

## Step 6: Check Output

When the script finishes, it creates two files in the current folder:

- `research_Note_taking_apps_comparison_YYYYMMDD_HHMMSS.xlsx` -- Excel workbook with multiple sheets (Summary, Posts, Comments, Entity Analysis, etc.)
- `research_Note_taking_apps_comparison_YYYYMMDD_HHMMSS.md` -- Markdown summary report

Open the Excel file to explore the data, or read the markdown report for a quick overview.

---

## Troubleshooting

### "No module named 'praw'"
The dependencies didn't install correctly. Try:
```bash
python3 -m pip install praw pandas openpyxl python-dotenv requests beautifulsoup4
```

### "Reddit credentials not found"
- Check that `.env` exists in the project folder (not inside a subfolder)
- Check there are no quotes around the values (use `KEY=value`, not `KEY="value"`)
- Check there are no trailing spaces after the values

### "401 Unauthorized" or "403 Forbidden"
- Double-check your client ID and client secret are correct
- Make sure you selected **"script"** type when creating the Reddit app
- Try regenerating the secret in your Reddit app settings

### ".env file not showing on Windows"
Windows hides files starting with a dot. Open it directly:
```bash
notepad .env
```

### "python3 not found" on Windows
Try `python` instead of `python3`, or `py -3`:
```bash
python reddit_research.py config_tutorial_example.json
```

---

## Running Research with Claude Code

The easiest way to use this tool is through [Claude Code](https://docs.anthropic.com/en/docs/claude-code), which generates configs for you from a plain English brief.

### Getting Started

1. Open Terminal in the project folder and start Claude Code:
   ```bash
   claude
   ```

2. Describe what you want to research. Claude will generate a JSON config, show it to you for review, and run the research when you're happy with it.

3. When it finishes, Claude can help you interpret the results -- just ask.

### Example Prompts

Here are some prompts to get you started:

**Product research:**
> I want to compare Philips Hue vs LIFX smart bulbs. What do people on Reddit think about reliability, brightness, and value for money?

**Company/brand sentiment:**
> Research what UK personal finance Reddit users think about Moneybox compared to Vanguard and Nutmeg. Focus on fees, app experience, and customer service.

**Market exploration:**
> What are people saying about mmWave radar sensors for home automation? I want to understand the main use cases and which products people recommend.

**Career research:**
> What advice does Reddit give about transitioning into product management? Track mentions of Google, Meta, Amazon, and Microsoft.

### Tips

- Be specific about what you care about -- Claude will pick better search terms and sentiment keywords
- Ask Claude to adjust the config if the first run returns too few or too many results
- You can also write configs manually -- see [CONFIG_GUIDE.md](../CONFIG_GUIDE.md) for the full field reference

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 reddit_research.py config.json` | Run research with a config |
| `pip3 install -r requirements.txt` | Install dependencies |
| `claude` | Start Claude Code assistant |

---

## Security Notes

- Never commit `.env` to git (it's already in `.gitignore`)
- The Reddit API is read-only with "script" type -- it can only read public posts, not post or modify anything
- Rate limited to ~60 requests/minute -- the script handles this automatically
