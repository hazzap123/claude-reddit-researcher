# Config File Guide

Reference for creating research config files.

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
- `"Moneybox investment app feedback"`

---

### `search_terms` (REQUIRED)
**Type:** Array of strings
**Purpose:** Search queries to find relevant posts

**Tips:**
- Use exact phrases that people would post
- Include product names, comparisons, reviews
- Add common misspellings or abbreviations
- Mix broad and specific terms

**Example:**
```json
"search_terms": [
  "iPhone vs Android",
  "best phone 2026",
  "iPhone 16 review",
  "switching from Android"
]
```

---

### `subreddits` (REQUIRED)
**Type:** Array of strings
**Purpose:** Specific communities to search
**Format:** Just the name (no `r/` prefix)

**Tips:**
- Mix general + niche communities
- Product subreddits often have more honest discussions
- Check subreddit size -- niche ones are more focused, large ones have more data

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
**Default:** `[]` (skip entity tracking)

**Tips:**
- Include your main subject + competitors
- Add common abbreviations (`PM` for Product Manager)
- The tool counts mentions and calculates sentiment per entity

**Example:**
```json
"entities_to_track": [
  "Moneybox",
  "Vanguard",
  "Nutmeg",
  "Freetrade"
]
```

**Output:** An Excel sheet showing total mentions, positive vs negative sentiment, and percentage breakdown per entity.

---

### `keywords_positive` (OPTIONAL)
**Type:** Array of strings
**Purpose:** Words indicating positive sentiment
**Default:** Built-in defaults including `great`, `excellent`, `love`, `perfect`, `best`, `amazing`, `recommend`, `helped`, `worked`, `worth it`, `game changer`

**Tips:**
- Add domain-specific positives: `intuitive`, `fast`, `reliable`
- Include action verbs: `switched to`, `upgraded to`
- Your keywords are added alongside the defaults

**Example:**
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
**Default:** Built-in defaults including `bad`, `terrible`, `hate`, `worst`, `avoid`, `waste`, `disappointed`, `useless`, `problem`, `issue`, `toxic`

**Tips:**
- Include complaints: `waste of money`, `buggy`
- Add frustration words: `frustrating`, `annoying`, `disappointed`
- Include action verbs: `switched away`, `cancelled`, `refunded`

**Example:**
```json
"keywords_negative": [
  "hate", "terrible", "avoid", "waste",
  "slow", "buggy", "expensive", "bloated",
  "switched away", "cancelled subscription"
]
```

---

### `limits` (OPTIONAL)
**Type:** Object with two numbers
**Purpose:** Control how much data to fetch
**Default:** `{"posts": 50, "comments": 3}`

**Structure:**
```json
"limits": {
  "posts": 25,
  "comments": 3
}
```

- `posts` -- Max posts fetched per search term + subreddit combination
- `comments` -- Max top-level comments fetched per post

**Rough calculation:**
```
Total entries ≈ (search_terms x subreddits x posts) + (posts x comments)
```

**Recommendations:**

| Use case | posts | comments | Approx. time |
|----------|-------|----------|--------------|
| Quick test | 10 | 2 | 2-5 min |
| Standard research | 25 | 3 | 5-10 min |
| Deep research | 50 | 5 | 15-30 min |

**Example:** 3 subreddits x 5 search terms x 25 posts = 375 posts. With 3 comments each = 1,125 comments. Total: ~1,500 entries.

---

### `include_all_reddit` (OPTIONAL)
**Type:** Boolean
**Purpose:** Also search across all of Reddit (not just your specified subreddits)
**Default:** `true`

**When to use:**
- You want to find discussions in unexpected places
- Your topic is broad and discussed everywhere
- You want to discover new relevant subreddits

**When to disable:**
- Topic is niche and specific
- You only care about particular communities
- Results are too noisy

---

### `all_reddit_limit` (OPTIONAL)
**Type:** Number
**Purpose:** Max posts to fetch when searching all of Reddit
**Default:** `10`
**Only applies if:** `include_all_reddit` is `true`

**Tip:** Keep this lower than `limits.posts` to avoid noise -- r/all results are broader and less targeted.

**Example:**
```json
"limits": {"posts": 25, "comments": 3},
"include_all_reddit": true,
"all_reddit_limit": 10
```

---

## Complete Examples

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
`"iPhone 15 battery life"` finds better discussions than `"iPhone"`.

### 3. Test Your Search Terms
Search Reddit manually first to see if your terms return good results.

### 4. Include Competitors
Entity tracking is most useful when comparing multiple options.

### 5. Domain-Specific Keywords
- **Finance:** `returns`, `fees`, `customer service`
- **Tech:** `buggy`, `intuitive`, `fast`, `crashes`
- **Products:** `worth it`, `waste of money`, `highly recommend`

### 6. Check Subreddit Rules
Some subreddits prohibit promotional content, so discussions tend to be more honest.

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
