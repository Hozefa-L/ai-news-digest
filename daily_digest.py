"""
AI News Daily Digest
Automated content curation system that monitors AI/tech news sources,
filters by relevance, extracts key information, generates summaries,
and publishes daily digests to Notion.

Free tier compatible: Tavily (1000 credits/mo), Groq (free), Notion API (free)
"""

import os
import json
from datetime import datetime, timezone
from typing import Optional
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

# API Keys (from environment variables)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Search Configuration
SEARCH_QUERY = "AI artificial intelligence LLM startup funding product launch"
SEARCH_TOPICS = ["AI", "LLM", "machine learning", "startup", "funding", "product launch", "OpenAI", "Anthropic", "Google AI", "Meta AI"]
MAX_ARTICLES = 10

# Topic tags for classification
TOPIC_TAGS = {
    "LLM": ["llm", "language model", "gpt", "claude", "gemini", "llama", "chatgpt", "chatbot"],
    "Funding": ["funding", "raised", "investment", "series a", "series b", "series c", "valuation", "investor"],
    "Startup": ["startup", "founded", "launch", "new company", "stealth"],
    "Product Launch": ["launch", "released", "announced", "introducing", "new feature", "update"],
    "Research": ["research", "paper", "study", "breakthrough", "discovered", "arxiv"],
    "Regulation": ["regulation", "law", "policy", "government", "eu ai act", "congress", "senate"],
    "Open Source": ["open source", "github", "hugging face", "weights", "apache", "mit license"],
}

# =============================================================================
# TAVILY API - Search & Extract
# =============================================================================

def tavily_search(query: str, max_results: int = 15) -> list[dict]:
    """
    Search for recent AI news using Tavily API.
    Cost: 2 credits (advanced search)
    """
    url = "https://api.tavily.com/search"
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",  # 2 credits, but better results
        "topic": "news",
        "days": 1,  # Last 24 hours
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        print(f"✓ Tavily search returned {len(results)} results")
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Tavily search error: {e}")
        return []


def tavily_extract(urls: list[str]) -> list[dict]:
    """
    Extract full content from URLs using Tavily API.
    Cost: 1 credit per 5 URLs (basic extraction)
    """
    if not urls:
        return []
    
    url = "https://api.tavily.com/extract"
    
    payload = {
        "api_key": TAVILY_API_KEY,
        "urls": urls[:MAX_ARTICLES],  # Limit to top articles
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        results = data.get("results", [])
        print(f"✓ Tavily extracted content from {len(results)} URLs")
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Tavily extract error: {e}")
        return []


# =============================================================================
# GROQ API - Summarization
# =============================================================================

def groq_summarize(article: dict) -> dict:
    """
    Generate a summary for a single article using Groq.
    Returns dict with summary and detected topics.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    title = article.get("title", "Untitled")
    content = article.get("raw_content", article.get("content", ""))[:8000]  # Limit content length
    source_url = article.get("url", "")
    
    prompt = f"""Analyze this AI/tech news article and provide:
1. A concise 2-3 sentence summary highlighting the key points
2. Classify it into one or more of these topics: LLM, Funding, Startup, Product Launch, Research, Regulation, Open Source

Article Title: {title}
Article Content: {content}

Respond in this exact JSON format:
{{"summary": "Your 2-3 sentence summary here", "topics": ["Topic1", "Topic2"]}}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a tech news analyst. Respond only with valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        content = data["choices"][0]["message"]["content"]
        
        # Parse JSON response
        try:
            result = json.loads(content)
            return {
                "title": title,
                "url": source_url,
                "summary": result.get("summary", "Summary unavailable"),
                "topics": result.get("topics", ["AI"]),
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "title": title,
                "url": source_url,
                "summary": content[:500],
                "topics": ["AI"],
            }
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Groq summarization error for '{title}': {e}")
        return {
            "title": title,
            "url": source_url,
            "summary": "Summary unavailable due to processing error.",
            "topics": ["AI"],
        }


def groq_generate_intro(summaries: list[dict]) -> str:
    """
    Generate an engaging introduction for the daily digest.
    """
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    # Create a brief overview of today's articles
    articles_overview = "\n".join([
        f"- {s['title']}: {s['summary'][:100]}..." 
        for s in summaries[:5]
    ])
    
    prompt = f"""Based on today's AI news articles, write a brief 2-3 sentence introduction for a daily digest newsletter. 
Be engaging and highlight the most significant theme or story of the day.

Today's top stories:
{articles_overview}

Write only the introduction paragraph, no headers or formatting."""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are a tech newsletter editor. Be concise and engaging."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 200,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Groq intro generation error: {e}")
        return "Here's your daily roundup of the most important AI and technology news."


# =============================================================================
# NOTION API - Publishing
# =============================================================================

def notion_create_digest(date: datetime, intro: str, summaries: list[dict], all_topics: set) -> bool:
    """
    Create a new digest entry in Notion database.
    """
    url = "https://api.notion.com/v1/pages"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }
    
    # Format date string
    date_str = date.strftime("%B %d, %Y")
    
    # Get top story
    top_story = summaries[0]["title"] if summaries else "No stories today"
    
    # Build page content blocks
    children_blocks = [
        # Introduction
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": intro}}]
            }
        },
        # Divider
        {"object": "block", "type": "divider", "divider": {}},
        # Section header
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"type": "text", "text": {"content": "📰 Today's Stories"}}]
            }
        },
    ]
    
    # Add each article summary
    for i, article in enumerate(summaries, 1):
        # Article title with link
        children_blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": f"{i}. {article['title'][:100]}",
                        "link": {"url": article["url"]} if article["url"] else None
                    }
                }]
            }
        })
        
        # Topics as callout
        topics_str = " • ".join([f"#{t.replace(' ', '')}" for t in article["topics"]])
        children_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": topics_str}, "annotations": {"color": "gray"}}
                ]
            }
        })
        
        # Summary
        children_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": article["summary"]}}]
            }
        })
        
        # Source link
        if article["url"]:
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "🔗 Read full article", "link": {"url": article["url"]}},
                        "annotations": {"color": "blue"}
                    }]
                }
            })
        
        # Spacer
        children_blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": []}
        })
    
    # Build the page payload
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": f"AI Digest - {date_str}"}}]
            },
            "Date": {
                "date": {"start": date.strftime("%Y-%m-%d")}
            },
            "Top Story": {
                "rich_text": [{"text": {"content": top_story[:2000]}}]  # Notion limit
            },
            "Topics": {
                "multi_select": [{"name": topic} for topic in list(all_topics)[:10]]
            },
            "Article Count": {
                "number": len(summaries)
            }
        },
        "children": children_blocks[:100]  # Notion limit of 100 blocks per request
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        page_url = data.get("url", "")
        print(f"✓ Notion digest created: {page_url}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Notion creation error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return False


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def validate_environment() -> bool:
    """Check that all required environment variables are set."""
    required_vars = [
        ("TAVILY_API_KEY", TAVILY_API_KEY),
        ("GROQ_API_KEY", GROQ_API_KEY),
        ("NOTION_API_KEY", NOTION_API_KEY),
        ("NOTION_DATABASE_ID", NOTION_DATABASE_ID),
    ]
    
    missing = [name for name, value in required_vars if not value]
    
    if missing:
        print(f"✗ Missing environment variables: {', '.join(missing)}")
        return False
    
    print("✓ All environment variables configured")
    return True


def run_daily_digest():
    """
    Main pipeline: Search → Extract → Summarize → Publish
    """
    print("=" * 60)
    print(f"🚀 AI News Daily Digest - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Step 0: Validate environment
    if not validate_environment():
        return False
    
    # Step 1: Search for AI news
    print("\n📡 Step 1: Searching for AI news...")
    search_results = tavily_search(SEARCH_QUERY, max_results=15)
    
    if not search_results:
        print("✗ No search results found. Exiting.")
        return False
    
    # Step 2: Extract full content from top articles
    print("\n📄 Step 2: Extracting article content...")
    urls = [r.get("url") for r in search_results if r.get("url")][:MAX_ARTICLES]
    extracted = tavily_extract(urls)
    
    # Merge search results with extracted content
    articles = []
    for search_result in search_results[:MAX_ARTICLES]:
        url = search_result.get("url", "")
        
        # Find matching extracted content
        extracted_content = next(
            (e for e in extracted if e.get("url") == url), 
            {}
        )
        
        articles.append({
            "title": search_result.get("title", "Untitled"),
            "url": url,
            "content": search_result.get("content", ""),
            "raw_content": extracted_content.get("raw_content", search_result.get("content", "")),
        })
    
    # Step 3: Generate summaries using Groq
    print(f"\n🤖 Step 3: Generating summaries for {len(articles)} articles...")
    summaries = []
    all_topics = set()
    
    for i, article in enumerate(articles, 1):
        print(f"   Processing {i}/{len(articles)}: {article['title'][:50]}...")
        summary = groq_summarize(article)
        summaries.append(summary)
        all_topics.update(summary.get("topics", []))
    
    print(f"✓ Generated {len(summaries)} summaries")
    print(f"✓ Topics covered: {', '.join(all_topics)}")
    
    # Step 4: Generate digest introduction
    print("\n✍️  Step 4: Generating digest introduction...")
    intro = groq_generate_intro(summaries)
    print(f"✓ Introduction: {intro[:100]}...")
    
    # Step 5: Publish to Notion
    print("\n📤 Step 5: Publishing to Notion...")
    today = datetime.now(timezone.utc)
    success = notion_create_digest(today, intro, summaries, all_topics)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Daily digest published successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ Failed to publish digest")
        print("=" * 60)
    
    return success


if __name__ == "__main__":
    success = run_daily_digest()
    exit(0 if success else 1)
