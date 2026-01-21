"""
AI News Daily Digest - Using Groq + Tavily MCP
Automated content curation system that uses Groq's Responses API with 
Tavily MCP for intelligent search, extraction, and summarization.

This demonstrates how Groq and Tavily MCP work together as an agentic system.
"""

import os
import json
import time
import re
from datetime import datetime, timezone
import requests

# =============================================================================
# CONFIGURATION
# =============================================================================

# API Keys (from environment variables)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Groq model that supports MCP tools
GROQ_MODEL = "compound-beta"  # Groq's compound model for tool use

# Search Configuration
MAX_ARTICLES = 10

# =============================================================================
# GROQ + TAVILY MCP - Agentic Search & Summarization
# =============================================================================

def groq_with_tavily_mcp(prompt: str, max_retries: int = 3) -> str:
    """
    Use Groq's Responses API with Tavily MCP tools.
    The LLM decides when and how to use Tavily search/extract.
    """
    url = "https://api.groq.com/openai/v1/responses"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Configure Tavily MCP as a tool
    tools = [{
        "type": "mcp",
        "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
        "server_label": "tavily",
        "require_approval": "never",
    }]
    
    payload = {
        "model": GROQ_MODEL,
        "input": prompt,
        "tools": tools,
        "temperature": 0.3,
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = (attempt + 1) * 10
                print(f"   ⏳ Rate limited, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # Extract the output text from the response
            output_text = data.get("output_text", "")
            if not output_text:
                # Try alternative response structure
                output = data.get("output", [])
                if output and isinstance(output, list):
                    for item in output:
                        if item.get("type") == "message":
                            content = item.get("content", [])
                            for c in content:
                                if c.get("type") == "text":
                                    output_text = c.get("text", "")
                                    break
            
            return output_text
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10
                print(f"   ⏳ Request error, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            print(f"✗ Groq MCP error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"  Response: {e.response.text[:500]}")
            return ""
    
    return ""


def search_and_curate_news() -> dict:
    """
    Use Groq + Tavily MCP to search for AI news and curate top stories.
    The LLM autonomously uses Tavily tools to find and analyze news.
    """
    
    prompt = f"""You are an AI news curator. Your task is to find and summarize today's top AI and technology news.

Use the tavily_search tool to search for recent AI news with these parameters:
- Query: "AI artificial intelligence LLM startup funding product launch"
- Topic: news
- Time range: day (last 24 hours)
- Max results: 15
- Search depth: advanced

After getting the search results, analyze them and create a curated digest with exactly {MAX_ARTICLES} articles.

For each article, provide:
1. Title
2. URL
3. A 2-3 sentence summary
4. Topics (classify as: LLM, Funding, Startup, Product Launch, Research, Regulation, Open Source)

Also write a brief 2-3 sentence introduction for the digest highlighting the day's most significant story or theme.

Format your response as JSON:
{{
    "introduction": "Your engaging intro here",
    "articles": [
        {{
            "title": "Article title",
            "url": "https://...",
            "summary": "2-3 sentence summary",
            "topics": ["Topic1", "Topic2"]
        }}
    ]
}}

Important: Return ONLY valid JSON, no markdown code blocks or other text."""

    print("🤖 Using Groq + Tavily MCP to search and curate news...")
    result = groq_with_tavily_mcp(prompt)
    
    if not result:
        return {"introduction": "", "articles": []}
    
    # Parse JSON from response
    try:
        # Clean up response - remove markdown code blocks if present
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
            cleaned = re.sub(r'\n?```$', '', cleaned)
        
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse JSON response: {e}")
        print(f"  Raw response: {result[:500]}...")
        return {"introduction": "", "articles": []}


# =============================================================================
# NOTION API - Publishing
# =============================================================================

def notion_create_digest(date: datetime, intro: str, articles: list[dict]) -> bool:
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
    
    # Get top story and all topics
    top_story = articles[0]["title"] if articles else "No stories today"
    all_topics = set()
    for article in articles:
        all_topics.update(article.get("topics", []))
    
    # Build page content blocks
    children_blocks = [
        # Introduction
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": intro}}],
                "icon": {"emoji": "🤖"},
                "color": "blue_background"
            }
        },
        # Powered by note
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": "Powered by "}, "annotations": {"italic": True, "color": "gray"}},
                    {"type": "text", "text": {"content": "Groq + Tavily MCP"}, "annotations": {"bold": True, "italic": True, "color": "gray"}},
                ]
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
    
    # Add each article
    for i, article in enumerate(articles, 1):
        title = article.get("title", "Untitled")[:100]
        article_url = article.get("url", "")
        summary = article.get("summary", "No summary available")
        topics = article.get("topics", ["AI"])
        
        # Article title with link
        children_blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": f"{i}. {title}",
                        "link": {"url": article_url} if article_url else None
                    }
                }]
            }
        })
        
        # Topics as tags
        topics_str = " • ".join([f"#{t.replace(' ', '')}" for t in topics])
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
                "rich_text": [{"type": "text", "text": {"content": summary}}]
            }
        })
        
        # Source link
        if article_url:
            children_blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "🔗 Read full article", "link": {"url": article_url}},
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
                "rich_text": [{"text": {"content": top_story[:2000]}}]
            },
            "Topics": {
                "multi_select": [{"name": topic} for topic in list(all_topics)[:10]]
            },
            "Article Count": {
                "number": len(articles)
            }
        },
        "children": children_blocks[:100]  # Notion limit
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
    Main pipeline using Groq + Tavily MCP agentic system.
    """
    print("=" * 60)
    print(f"🚀 AI News Daily Digest (Groq + Tavily MCP)")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # Step 0: Validate environment
    if not validate_environment():
        return False
    
    # Step 1: Search and curate news using Groq + Tavily MCP
    print("\n📡 Step 1: Searching and curating AI news via MCP...")
    digest_data = search_and_curate_news()
    
    introduction = digest_data.get("introduction", "")
    articles = digest_data.get("articles", [])
    
    if not articles:
        print("✗ No articles found. Exiting.")
        return False
    
    print(f"✓ Curated {len(articles)} articles")
    
    # Collect all topics
    all_topics = set()
    for article in articles:
        all_topics.update(article.get("topics", []))
    print(f"✓ Topics covered: {', '.join(all_topics)}")
    
    if introduction:
        print(f"✓ Introduction: {introduction[:100]}...")
    
    # Step 2: Publish to Notion
    print("\n📤 Step 2: Publishing to Notion...")
    today = datetime.now(timezone.utc)
    
    if not introduction:
        introduction = "Here's your daily roundup of the most important AI and technology news."
    
    success = notion_create_digest(today, introduction, articles)
    
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
