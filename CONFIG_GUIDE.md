# Config File Guide

Quick reference for creating research config files.

---

## Basic Structure

```json
{
  "topic": "Your research topic",
  "search_terms": ["query 1", "query 2"],
  "subreddits": ["subreddit1", "subreddit2"],
  "entities_to_track": ["Entity 1", "Entity 2"],
  "keywords_positive": ["good", "great"],
  "keywords_negative": ["bad", "terrible"],
  "limits": {"posts": 25, "comments": 3},
  "include_all_reddit": true,
  "all_reddit_limit": 10
}
```

---

## Field Explanations

### `topic` (REQUIRED)
**Type:** String
**Purpose:** Main research question or topic name
**Used for:** Output filenames, report headers

**Examples:**
- `"Best smart bulbs 2026"`
- `"Product manager career advice"`
- `"Competitive egg and spoon top tips"`

---

### `search_terms` (OPTIONAL)
**Type:** Array of strings
**Purpose:** Search queries to find relevant posts
**Default:** `[]` (skip search if empty)

**Tips:**
- Use exact phrases that people would post
- Include product names, comparisons, reviews
- Add common misspellings or abbreviations
- Mix broad and specific terms

**Examples:**
```json
"search_terms": [
  "iPhone vs Android",           // Comparison
  "best phone 2026",            // General query
  "iPhone 16 review",           // Specific product
  "switching from Android"      // User intent
]
```

---

### `subreddits` (OPTIONAL)
**Type:** Array of strings
**Purpose:** Specific communities to search
**Format:** Just the name (no `r/` prefix)
**Default:** `[]` (skip if empty)

**Tips:**
- Mix general + niche communities
- Check subreddit size (r/all has millions, niche ones are more focused)
- Product subreddits often have honest discussions

**Common Subreddits by Topic:**

| Topic | Subreddits |
|-------|-----------|
| Tech Products | `technology`, `gadgets`, `BuyItForLife` |
| Finance Apps | `UKPersonalFinance`, `UKInvesting`, `FIREUK` |
| Productivity | `productivity`, `GTD`, `Notion`, `ObsidianMD` |
| Smart Home | `homeassistant`, `smarthome`, `homeautomation` |
| Career | `cscareerquestions`, `experienceddevs`, `ProductManagement` |

---

### `entities_to_track` (OPTIONAL)
**Type:** Array of strings
**Purpose:** Track mentions of companies, products, or people
**Matching:** Case-insensitive
**Default:** `[]` (skip entity tracking if empty)

**Tips:**
- Include your main subject + competitors
- Add common abbreviations (`PM` for Product Manager)
- Tool counts mentions and calculates sentiment per entity

**Examples:**
```json
"entities_to_track": [
  "Moneybox",          // Your research target
  "Vanguard",          // Competitor 1
  "Nutmeg",            // Competitor 2
  "Freetrade"          // Competitor 3
]
```

**Output:** Excel sheet showing:
- Total mentions per entity
- Positive vs negative sentiment
- Percentage breakdown

---

### `keywords_positive` (OPTIONAL)
**Type:** Array of strings
**Purpose:** Words indicating positive sentiment
**Default:** `[]` (basic sentiment only)

**Tips:**
- Include enthusiastic words: `amazing`, `love`, `highly recommend`
- Add action verbs: `switched to`, `upgraded to`
- Use domain-specific positives: `intuitive`, `fast`, `reliable`

**Examples:**
```json
"keywords_positive": [
  "love", "great", "best", "recommend",
  "game changer", "worth it", "switched to",
  "finally", "perfect", "exactly what I needed"
]
```

---

### `keywords_negative` (OPTIONAL)
**Type:** Array of strings
**Purpose:** Words indicating negative sentiment
**Default:** `[]` (basic sentiment only)

**Tips:**
- Include complaints: `terrible`, `waste of money`, `buggy`
- Add frustration words: `frustrating`, `annoying`, `disappointed`
- Use action verbs: `switched away`, `cancelled`, `refunded`

**Examples:**
```json
"keywords_negative": [
  "hate", "terrible", "avoid", "waste",
  "slow", "buggy", "expensive", "bloated",
  "switched away", "cancelled subscription"
]
```

---

### `limits` (REQUIRED)
**Type:** Object with two numbers
**Purpose:** Control how much data to fetch (API rate limiting)

**Structure:**
```json
"limits": {
  "posts": 25,      // Max posts per search_term + subreddit combo
  "comments": 3     // Max top-level comments per post
}
```

**Calculation:**
```
Total API calls ≈ (search_terms × subreddits × posts) + (posts × comments)
```

**Recommendations:**
- **Quick test:** `"posts": 10, "comments": 2` (~2-5 min)
- **Standard research:** `"posts": 25, "comments": 3` (~5-10 min)
- **Deep research:** `"posts": 50, "comments": 5` (~15-30 min)

**Example:**
- 3 subreddits × 5 search terms × 25 posts = 375 posts
- 375 posts × 3 comments = 1,125 comments
- **Total entries:** ~1,500

---

### `include_all_reddit` (OPTIONAL)
**Type:** Boolean
**Purpose:** Search across ALL of Reddit (not just specified subreddits)
**Default:** `false`

**When to use:**
- You want to find discussions in unexpected places
- Your topic is broad and discussed everywhere
- You want to discover new relevant subreddits

**When to skip:**
- Topic is niche and specific
- You only care about particular communities
- Results are too noisy

---

### `all_reddit_limit` (OPTIONAL)
**Type:** Number
**Purpose:** Max posts when searching all of Reddit
**Default:** `0` (disabled)
**Only applies if:** `include_all_reddit: true`

**Tip:** Keep lower than subreddit `limits.posts` to avoid noise

**Example:**
```json
"limits": {"posts": 25, "comments": 3},
"include_all_reddit": true,
"all_reddit_limit": 10           // Only 10 from r/all
```

---

## Complete Examples

### Minimal Config (topic only)
```json
{
  "topic": "Quick test"
}
```
This will work but won't collect much data.

---

### Product Research
```json
{
  "topic": "Philips Hue vs LIFX smart bulbs",
  "search_terms": [
    "Philips Hue review",
    "LIFX review",
    "Hue vs LIFX",
    "best smart bulbs"
  ],
  "subreddits": ["homeassistant", "smarthome", "Hue", "lifx"],
  "entities_to_track": ["Philips Hue", "LIFX", "Nanoleaf", "IKEA"],
  "keywords_positive": ["love", "reliable", "bright", "worth it"],
  "keywords_negative": ["unreliable", "expensive", "buggy", "disconnects"],
  "limits": {"posts": 30, "comments": 5},
  "include_all_reddit": true,
  "all_reddit_limit": 15
}
```

---

### Company/Brand Research
```json
{
  "topic": "Moneybox investment app feedback",
  "search_terms": [
    "Moneybox review",
    "Moneybox app",
    "Moneybox vs Vanguard",
    "best investment app UK"
  ],
  "subreddits": ["UKPersonalFinance", "UKInvesting", "FIREUK"],
  "entities_to_track": ["Moneybox", "Vanguard", "Nutmeg", "Trading 212"],
  "keywords_positive": ["easy to use", "great returns", "recommend"],
  "keywords_negative": ["high fees", "poor customer service", "slow"],
  "limits": {"posts": 50, "comments": 5},
  "include_all_reddit": false
}
```

---

### Career/Topic Research
```json
{
  "topic": "Product Manager career path",
  "search_terms": [
    "how to become PM",
    "product manager career",
    "PM interview tips",
    "transitioning to PM"
  ],
  "subreddits": ["ProductManagement", "cscareerquestions"],
  "entities_to_track": ["Google", "Meta", "Amazon", "Microsoft"],
  "keywords_positive": ["got the job", "successful", "great advice"],
  "keywords_negative": ["rejected", "difficult", "burnout"],
  "limits": {"posts": 40, "comments": 4},
  "include_all_reddit": true,
  "all_reddit_limit": 20
}
```

---

## Tips for Better Results

### 1. Start Small, Scale Up
Run with `"posts": 10` first to test your search terms, then increase.

### 2. Specific > General
`"iPhone 15 battery life"` finds better discussions than `"iPhone"`

### 3. Test Your Search Terms
Search Reddit manually first to see if your terms return good results.

### 4. Include Competitors
Entity tracking is most useful when comparing multiple options.

### 5. Domain-Specific Keywords
Finance: `returns`, `fees`, `customer service`
Tech: `buggy`, `intuitive`, `fast`, `crashes`
Products: `worth it`, `waste of money`, `highly recommend`

### 6. Check Subreddit Rules
Some subreddits prohibit promotional content, so discussions are more honest.

---

## Troubleshooting

**Too few results?**
- Add more search terms
- Add more subreddits
- Enable `include_all_reddit`
- Increase `limits.posts`

**Too many irrelevant results?**
- Make search terms more specific
- Remove broad subreddits
- Disable `include_all_reddit`

**Poor sentiment detection?**
- Add more `keywords_positive` and `keywords_negative`
- Use domain-specific language

**Script running too long?**
- Decrease `limits.posts`
- Decrease `limits.comments`
- Reduce number of `search_terms`

---

## File Naming

Save configs with descriptive names:
- `config_moneybox.json`
- `config_smart_bulbs.json`
- `config_pm_careers.json`

Keep them organized in an `output/` or `configs/` folder.
