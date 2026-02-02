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
  "limits": {"posts": 50, "comments": 3}
}
```

## Common Subreddits by Topic

| Topic | Subreddits |
|-------|------------|
| Product Management | ProductManagement, prodmgmt |
| Startups | startups, Entrepreneur, SaaS |
| Tech Careers | cscareerquestions, experienceddevs |
| Data/Analytics | dataengineering, datascience, analytics |
| UK Finance | UKPersonalFinance, FIREUK, UKInvesting |
| Smart Home | homeassistant, smarthome, homeautomation |
| General Tech | technology, gadgets |

## Setup (One-Time)

1. **Install Python packages:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Get Reddit API keys:**
   - Go to reddit.com/prefs/apps
   - Create app → select "script" type
   - Copy client_id and secret

3. **Create .env file:**
   ```
   REDDIT_CLIENT_ID=xxxxx
   REDDIT_CLIENT_SECRET=xxxxx
   REDDIT_USER_AGENT=ResearchTool/1.0 by YourUsername
   ```

## Output Files

| File | Contains |
|------|----------|
| `research_*.xlsx` | All data + analysis sheets |
| `research_*.md` | Summary report |
| `output/research_output.json` | Machine-readable metadata |

## Tips

- Start with small `limits` (10-20 posts) to test
- More specific search terms = better results
- Check Entity Analysis sheet for competitor insights
- Use Positive Highlights sheet for testimonials/case studies
