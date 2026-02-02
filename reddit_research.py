#!/usr/bin/env python3
"""
Unified Reddit Research Tool
Configurable research automation for any domain: roles, projects, products, health, etc.
"""

import os
import json
import sys
import re
import time
from datetime import datetime
from pathlib import Path

try:
    import praw
    import pandas as pd
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("\nInstall required packages:")
    print("pip install praw pandas openpyxl python-dotenv")
    sys.exit(1)

load_dotenv()

REDDIT_CONFIG = {
    'client_id': os.getenv('REDDIT_CLIENT_ID'),
    'client_secret': os.getenv('REDDIT_CLIENT_SECRET'),
    'user_agent': os.getenv('REDDIT_USER_AGENT', 'Research Tool v2.0')
}

# ============================================
# CONFIGURATION
# ============================================

DEFAULT_CONFIG = {
    'topic': '',
    'search_terms': [],
    'subreddits': [],
    'entities_to_track': [],
    'keywords_positive': ['great', 'excellent', 'love', 'perfect', 'best', 'amazing',
                          'recommend', 'helped', 'worked', 'worth it', 'game changer'],
    'keywords_negative': ['bad', 'terrible', 'hate', 'worst', 'avoid', 'waste',
                          'disappointed', 'useless', 'problem', 'issue', 'toxic'],
    'limits': {'posts': 50, 'comments': 3},
    'include_all_reddit': True,
    'all_reddit_limit': 10
}


def load_config(config_path=None):
    """Load and validate research configuration."""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    elif not sys.stdin.isatty():
        config = json.loads(sys.stdin.read())
    else:
        print("ERROR: No configuration provided")
        print("Usage: python reddit_research.py config.json")
        print("   or: echo '{...}' | python reddit_research.py")
        sys.exit(1)

    # Validate required fields
    required = ['topic', 'search_terms', 'subreddits']
    missing = [f for f in required if f not in config or not config[f]]
    if missing:
        print(f"ERROR: Missing required fields: {', '.join(missing)}")
        sys.exit(1)

    # Merge with defaults
    merged = DEFAULT_CONFIG.copy()
    merged.update(config)

    return merged


# ============================================
# REDDIT API
# ============================================

def init_reddit():
    """Initialize Reddit API connection."""
    if not REDDIT_CONFIG['client_id']:
        print("\nERROR: Reddit credentials not found")
        print("Create a .env file with:")
        print("  REDDIT_CLIENT_ID=xxx")
        print("  REDDIT_CLIENT_SECRET=xxx")
        print("  REDDIT_USER_AGENT=xxx")
        print("\nGet credentials at: https://www.reddit.com/prefs/apps")
        sys.exit(1)

    print("Connecting to Reddit API...")
    reddit = praw.Reddit(
        client_id=REDDIT_CONFIG['client_id'],
        client_secret=REDDIT_CONFIG['client_secret'],
        user_agent=REDDIT_CONFIG['user_agent']
    )
    print(f"✓ Connected (read-only: {reddit.read_only})")
    return reddit


def safe_get(obj, attr, default=''):
    """Safely get attribute with fallback."""
    try:
        value = getattr(obj, attr, default)
        return value if value is not None else default
    except:
        return default


# ============================================
# SCRAPING
# ============================================

def scrape_subreddit(reddit, subreddit_name, search_term, post_limit, comment_limit):
    """Scrape posts and comments from a subreddit search."""
    results = []

    try:
        subreddit = reddit.subreddit(subreddit_name)
        search_results = subreddit.search(search_term, limit=post_limit, sort='relevance')

        for submission in search_results:
            try:
                # Post data
                author = '[deleted]'
                try:
                    if submission.author:
                        author = str(submission.author.name)
                except:
                    pass

                post = {
                    'id': safe_get(submission, 'id'),
                    'type': 'post',
                    'subreddit': safe_get(submission.subreddit, 'display_name', subreddit_name),
                    'title': safe_get(submission, 'title'),
                    'text': safe_get(submission, 'selftext'),
                    'author': author,
                    'score': safe_get(submission, 'score', 0),
                    'upvote_ratio': safe_get(submission, 'upvote_ratio', 0),
                    'num_comments': safe_get(submission, 'num_comments', 0),
                    'created_utc': submission.created_utc if hasattr(submission, 'created_utc') else 0,
                    'url': f"https://reddit.com{submission.permalink}" if hasattr(submission, 'permalink') else '',
                    'search_term': search_term
                }
                results.append(post)

                # Comments
                try:
                    submission.comments.replace_more(limit=0)
                    for comment in submission.comments[:comment_limit]:
                        if not hasattr(comment, 'body'):
                            continue

                        comment_author = '[deleted]'
                        try:
                            if comment.author:
                                comment_author = str(comment.author.name)
                        except:
                            pass

                        results.append({
                            'id': safe_get(comment, 'id'),
                            'type': 'comment',
                            'subreddit': post['subreddit'],
                            'title': '',
                            'text': safe_get(comment, 'body'),
                            'author': comment_author,
                            'score': safe_get(comment, 'score', 0),
                            'upvote_ratio': 0,
                            'num_comments': 0,
                            'created_utc': comment.created_utc if hasattr(comment, 'created_utc') else 0,
                            'url': f"{post['url']}{comment.id}" if post['url'] else '',
                            'search_term': search_term,
                            'parent_id': post['id'],
                            'parent_title': post['title']
                        })
                except:
                    pass

            except:
                continue

    except Exception as e:
        print(f"    Error: {e}")

    return results


def collect_data(reddit, config):
    """Collect all data based on configuration."""
    all_results = []
    seen_ids = set()

    subreddits = config['subreddits']
    search_terms = config['search_terms']
    post_limit = config['limits']['posts']
    comment_limit = config['limits']['comments']

    total = len(subreddits) * len(search_terms)
    current = 0

    print(f"\nSearching {total} subreddit/term combinations...")

    for subreddit in subreddits:
        for term in search_terms:
            current += 1
            print(f"[{current}/{total}] r/{subreddit}: '{term[:40]}..'" if len(term) > 40 else f"[{current}/{total}] r/{subreddit}: '{term}'", end='')

            results = scrape_subreddit(reddit, subreddit, term, post_limit, comment_limit)

            # Deduplicate
            new_count = 0
            for r in results:
                key = f"{r['id']}_{r['type']}"
                if key not in seen_ids:
                    seen_ids.add(key)
                    all_results.append(r)
                    new_count += 1

            posts = sum(1 for r in results if r['type'] == 'post' and f"{r['id']}_post" not in seen_ids or f"{r['id']}_post" in seen_ids)
            print(f" → {new_count} new")
            time.sleep(0.5)  # Rate limiting

    # Search all of Reddit for priority terms
    if config.get('include_all_reddit', True):
        print("\nSearching all of Reddit...")
        priority_terms = search_terms[:5]

        for term in priority_terms:
            print(f"  all: '{term[:40]}..'" if len(term) > 40 else f"  all: '{term}'", end='')

            results = scrape_subreddit(reddit, 'all', term, config.get('all_reddit_limit', 10), comment_limit)

            new_count = 0
            for r in results:
                key = f"{r['id']}_{r['type']}"
                if key not in seen_ids:
                    seen_ids.add(key)
                    all_results.append(r)
                    new_count += 1

            print(f" → {new_count} new")
            time.sleep(0.5)

    return all_results


# ============================================
# ANALYSIS
# ============================================

def find_entities(text, entities):
    """Find which entities are mentioned in text."""
    text_lower = text.lower()
    return [e for e in entities if e.lower() in text_lower]


def classify_sentiment(text, positive_kw, negative_kw):
    """Classify sentiment based on keyword matches."""
    text_lower = text.lower()
    pos = sum(1 for kw in positive_kw if kw.lower() in text_lower)
    neg = sum(1 for kw in negative_kw if kw.lower() in text_lower)

    if pos > neg:
        return 'Positive'
    elif neg > pos:
        return 'Negative'
    return 'Neutral'


def analyze_data(df, config):
    """Perform comprehensive analysis."""
    entities = config.get('entities_to_track', [])
    pos_kw = config.get('keywords_positive', [])
    neg_kw = config.get('keywords_negative', [])

    # Add analysis columns
    df['full_text'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
    df['entities_mentioned'] = df['full_text'].apply(lambda x: ', '.join(find_entities(x, entities)))
    df['sentiment'] = df['full_text'].apply(lambda x: classify_sentiment(x, pos_kw, neg_kw))
    df['created_date'] = pd.to_datetime(df['created_utc'], unit='s').dt.strftime('%Y-%m-%d')
    df['created_time'] = pd.to_datetime(df['created_utc'], unit='s').dt.strftime('%H:%M:%S')

    analysis = {}

    # Entity analysis
    entity_counts = {}
    entity_sentiment = {}

    for entity in entities:
        mask = df['full_text'].str.lower().str.contains(entity.lower(), regex=False)
        count = mask.sum()
        if count > 0:
            entity_counts[entity] = int(count)
            sentiment_counts = df[mask]['sentiment'].value_counts().to_dict()
            entity_sentiment[entity] = {
                'Positive': sentiment_counts.get('Positive', 0),
                'Negative': sentiment_counts.get('Negative', 0),
                'Neutral': sentiment_counts.get('Neutral', 0),
                'total': int(count)
            }

    analysis['entities'] = entity_counts
    analysis['entity_sentiment'] = entity_sentiment

    # Overall sentiment
    sentiment_counts = df['sentiment'].value_counts().to_dict()
    analysis['sentiment'] = {
        'Positive': sentiment_counts.get('Positive', 0),
        'Negative': sentiment_counts.get('Negative', 0),
        'Neutral': sentiment_counts.get('Neutral', 0)
    }

    # Subreddit performance
    posts_df = df[df['type'] == 'post']
    subreddit_stats = posts_df.groupby('subreddit').agg({
        'id': 'count',
        'score': 'mean',
        'num_comments': 'mean'
    }).round(2)
    subreddit_stats.columns = ['posts', 'avg_score', 'avg_comments']
    subreddit_stats = subreddit_stats.sort_values('posts', ascending=False)
    analysis['subreddits'] = subreddit_stats.to_dict('index')

    # Top posts
    top_posts = posts_df.nlargest(10, 'score')[['title', 'subreddit', 'score', 'num_comments', 'url', 'sentiment']].to_dict('records')
    analysis['top_posts'] = top_posts

    # Engagement
    analysis['engagement'] = {
        'total_posts': len(posts_df),
        'total_comments': len(df[df['type'] == 'comment']),
        'avg_score': round(df['score'].mean(), 2),
        'total_score': int(df['score'].sum())
    }

    # Date range
    dates = pd.to_datetime(df['created_utc'], unit='s')
    analysis['date_range'] = {
        'earliest': dates.min().strftime('%Y-%m-%d'),
        'latest': dates.max().strftime('%Y-%m-%d')
    }

    return df, analysis


# ============================================
# EXPORT
# ============================================

def export_excel(df, config, analysis, output_path):
    """Export results to Excel with multiple sheets."""

    posts_df = df[df['type'] == 'post'].copy()
    comments_df = df[df['type'] == 'comment'].copy()

    # Columns to export
    post_cols = ['id', 'subreddit', 'title', 'text', 'author', 'score', 'upvote_ratio',
                 'num_comments', 'created_date', 'url', 'entities_mentioned', 'sentiment']
    comment_cols = ['id', 'subreddit', 'parent_title', 'text', 'author', 'score',
                    'created_date', 'url', 'entities_mentioned', 'sentiment']

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

        # Summary sheet
        summary = {
            'Metric': [
                'Topic',
                'Total Posts',
                'Total Comments',
                'Unique Subreddits',
                'Date Range',
                'Average Score',
                'Total Engagement',
                'Positive Posts',
                'Negative Posts',
                'Neutral Posts',
                'Entities Tracked',
                'Posts with Entity Mentions'
            ],
            'Value': [
                config['topic'],
                analysis['engagement']['total_posts'],
                analysis['engagement']['total_comments'],
                len(analysis['subreddits']),
                f"{analysis['date_range']['earliest']} to {analysis['date_range']['latest']}",
                analysis['engagement']['avg_score'],
                analysis['engagement']['total_score'],
                analysis['sentiment']['Positive'],
                analysis['sentiment']['Negative'],
                analysis['sentiment']['Neutral'],
                len(config.get('entities_to_track', [])),
                len(df[df['entities_mentioned'] != ''])
            ]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)

        # Posts sheet
        posts_export = posts_df[[c for c in post_cols if c in posts_df.columns]].sort_values('score', ascending=False)
        posts_export.to_excel(writer, sheet_name='Posts', index=False)

        # Comments sheet
        comments_export = comments_df[[c for c in comment_cols if c in comments_df.columns]].sort_values('score', ascending=False)
        comments_export.to_excel(writer, sheet_name='Comments', index=False)

        # Entity analysis
        if analysis['entities']:
            entity_data = []
            for entity, count in sorted(analysis['entities'].items(), key=lambda x: -x[1]):
                sent = analysis['entity_sentiment'].get(entity, {})
                total = sent.get('total', count)
                pos = sent.get('Positive', 0)
                entity_data.append({
                    'Entity': entity,
                    'Mentions': count,
                    'Positive': pos,
                    'Negative': sent.get('Negative', 0),
                    'Neutral': sent.get('Neutral', 0),
                    'Positive %': round(pos / total * 100, 1) if total > 0 else 0
                })
            pd.DataFrame(entity_data).to_excel(writer, sheet_name='Entity Analysis', index=False)

        # Subreddit stats
        sub_data = [{'Subreddit': k, **v} for k, v in analysis['subreddits'].items()]
        pd.DataFrame(sub_data).to_excel(writer, sheet_name='Subreddit Stats', index=False)

        # Top posts
        pd.DataFrame(analysis['top_posts']).to_excel(writer, sheet_name='Top Posts', index=False)

        # High-value posts (positive sentiment, good score)
        high_value = posts_df[(posts_df['sentiment'] == 'Positive') & (posts_df['score'] >= 5)]
        if len(high_value) > 0:
            high_value[[c for c in post_cols if c in high_value.columns]].to_excel(
                writer, sheet_name='Positive Highlights', index=False
            )

    return output_path


def export_report(config, analysis, output_path):
    """Generate markdown report."""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Reddit Research Report: {config['topic']}\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")

        # Summary
        f.write("## Summary\n\n")
        f.write(f"- **Posts collected:** {analysis['engagement']['total_posts']}\n")
        f.write(f"- **Comments collected:** {analysis['engagement']['total_comments']}\n")
        f.write(f"- **Subreddits:** {len(analysis['subreddits'])}\n")
        f.write(f"- **Date range:** {analysis['date_range']['earliest']} to {analysis['date_range']['latest']}\n")
        f.write(f"- **Total engagement:** {analysis['engagement']['total_score']} points\n\n")

        # Sentiment
        f.write("## Sentiment Overview\n\n")
        total = sum(analysis['sentiment'].values())
        for sentiment, count in analysis['sentiment'].items():
            pct = round(count / total * 100, 1) if total > 0 else 0
            f.write(f"- **{sentiment}:** {count} ({pct}%)\n")
        f.write("\n")

        # Entities
        if analysis['entities']:
            f.write("## Entity Analysis\n\n")
            f.write("| Entity | Mentions | Positive | Negative | Positive % |\n")
            f.write("|--------|----------|----------|----------|------------|\n")
            for entity, count in sorted(analysis['entities'].items(), key=lambda x: -x[1])[:15]:
                sent = analysis['entity_sentiment'].get(entity, {})
                pos = sent.get('Positive', 0)
                neg = sent.get('Negative', 0)
                total = sent.get('total', count)
                pct = round(pos / total * 100, 1) if total > 0 else 0
                f.write(f"| {entity} | {count} | {pos} | {neg} | {pct}% |\n")
            f.write("\n")

        # Top subreddits
        f.write("## Top Subreddits\n\n")
        for sub, stats in list(analysis['subreddits'].items())[:10]:
            f.write(f"- **r/{sub}**: {stats['posts']} posts, avg score {stats['avg_score']}\n")
        f.write("\n")

        # Top posts
        f.write("## Top Posts\n\n")
        for i, post in enumerate(analysis['top_posts'][:10], 1):
            title = post['title'][:80] + '...' if len(post['title']) > 80 else post['title']
            f.write(f"{i}. [{title}]({post['url']}) - {post['score']} pts, {post['sentiment']}\n")
        f.write("\n")

        f.write("---\n")
        f.write(f"*Generated by Reddit Research Tool*\n")

    return output_path


# ============================================
# MAIN
# ============================================

def main():
    print("\n" + "="*60)
    print("REDDIT RESEARCH TOOL")
    print("="*60)

    # Load config
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    config = load_config(config_path)

    print(f"\n📋 Topic: {config['topic']}")
    print(f"🔍 Search terms: {len(config['search_terms'])}")
    print(f"📍 Subreddits: {', '.join(config['subreddits'])}")
    print(f"🏷️  Entities to track: {len(config.get('entities_to_track', []))}")

    # Connect
    reddit = init_reddit()

    # Scrape
    results = collect_data(reddit, config)

    if not results:
        print("\n✗ No results found")
        sys.exit(1)

    print(f"\n✓ Collected {len(results)} total entries")

    # Analyze
    print("\nAnalyzing data...")
    df = pd.DataFrame(results)
    df, analysis = analyze_data(df, config)

    # Export
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    topic_slug = re.sub(r'[^\w\s-]', '', config['topic'])[:30].strip().replace(' ', '_')

    excel_path = f"research_{topic_slug}_{timestamp}.xlsx"
    report_path = f"research_{topic_slug}_{timestamp}.md"

    print(f"\nExporting results...")
    export_excel(df, config, analysis, excel_path)
    export_report(config, analysis, report_path)

    # Summary
    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)
    print(f"\n📊 Posts: {analysis['engagement']['total_posts']}")
    print(f"💬 Comments: {analysis['engagement']['total_comments']}")
    print(f"😊 Sentiment: +{analysis['sentiment']['Positive']} / -{analysis['sentiment']['Negative']}")

    if analysis['entities']:
        top_entity = max(analysis['entities'].items(), key=lambda x: x[1])
        print(f"🏆 Top entity: {top_entity[0]} ({top_entity[1]} mentions)")

    print(f"\n📁 Excel: {excel_path}")
    print(f"📄 Report: {report_path}")

    # Output JSON for programmatic use
    output = {
        'excel_file': excel_path,
        'report_file': report_path,
        'posts': analysis['engagement']['total_posts'],
        'comments': analysis['engagement']['total_comments'],
        'sentiment': analysis['sentiment'],
        'top_entities': dict(sorted(analysis['entities'].items(), key=lambda x: -x[1])[:5])
    }

    with open('research_output.json', 'w') as f:
        json.dump(output, f, indent=2)


if __name__ == '__main__':
    main()
