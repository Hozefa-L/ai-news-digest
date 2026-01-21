"""
AI News Daily Digest - Using Groq + Tavily MCP
Automated content curation system that uses Groq's Responses API with 
Tavily MCP for intelligent search, extraction, and summarization.

This demonstrates how Groq and Tavily MCP work together as an agentic system.
Output: Markdown files saved to the repository (digests/ folder)
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

# Groq model that supports MCP tools (from Groq docs)
GROQ_MODEL = "openai/gpt-oss-120b"

# Search Configuration
MAX_ARTICLES = 10

# Output directory for digests
DIGEST_DIR = "digests"

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
    
    # Configure Tavily MCP as a tool (from Groq docs)
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
        "temperature": 0.1,
        "top_p": 0.4,
    }
    
    for attempt in range(max_retries):
        try:
            print(f"   Calling Groq Responses API (attempt {attempt + 1})...")
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = (attempt + 1) * 15
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
                                if c.get("type") == "output_text":
                                    output_text = c.get("text", "")
                                    break
                                elif c.get("type") == "text":
                                    output_text = c.get("text", "")
                                    break
            
            if not output_text:
                # Last resort - just get any text content
                output_text = json.dumps(data)
                print(f"   Debug - Raw response structure: {list(data.keys())}")
            
            return output_text
            
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 15
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
    
    # Clear, explicit prompt that instructs using ONLY tavily_search
    prompt = f"""You have access to the Tavily MCP server. You MUST use the tavily_search tool to complete this task.

STEP 1: Call the tavily_search tool with these EXACT parameters:
{{
    "query": "AI artificial intelligence machine learning news today",
    "topic": "news",
    "days": 1,
    "max_results": 15,
    "search_depth": "basic"
}}

STEP 2: After receiving the search results, analyze them and select the {MAX_ARTICLES} most important and diverse stories about AI/ML.

STEP 3: Format your response as a JSON object with this structure:
{{
    "introduction": "A 2-3 sentence engaging introduction highlighting the day's most significant AI story or theme",
    "articles": [
        {{
            "title": "The article headline",
            "url": "https://the-source-url.com/article",
            "summary": "A 2-3 sentence summary of the key points",
            "topics": ["Topic1", "Topic2"]
        }}
    ]
}}

For topics, use these categories: LLM, Funding, Startup, Product Launch, Research, Regulation, Open Source, Hardware, Robotics, AI Safety

IMPORTANT INSTRUCTIONS:
- Use ONLY the tavily_search tool (do NOT use tavily_extract or any other tools)
- Return ONLY valid JSON in your final response, no markdown code blocks
- Include exactly {MAX_ARTICLES} articles in your response
- Use the actual URLs from the search results"""

    print("🤖 Using Groq + Tavily MCP to search and curate news...")
    result = groq_with_tavily_mcp(prompt)
    
    if not result:
        return {"introduction": "", "articles": []}
    
    # Parse JSON from response
    try:
        # Clean up response - remove markdown code blocks if present
        cleaned = result.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\n?', '', cleaned)
            cleaned = re.sub(r'\n?```$', '', cleaned)
        
        # Find JSON in the response
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            cleaned = json_match.group()
        
        data = json.loads(cleaned)
        print(f"   ✓ Successfully parsed response")
        return data
    except json.JSONDecodeError as e:
        print(f"✗ Failed to parse JSON response: {e}")
        print(f"  Raw response (first 1000 chars): {result[:1000]}...")
        return {"introduction": "", "articles": []}


# =============================================================================
# MARKDOWN OUTPUT - Save digest as a markdown file
# =============================================================================

def save_digest_markdown(date: datetime, intro: str, articles: list[dict]) -> str:
    """
    Save the digest as a beautifully formatted Markdown file.
    Returns the path to the saved file.
    """
    # Create digests directory if it doesn't exist
    os.makedirs(DIGEST_DIR, exist_ok=True)
    
    # Format date strings
    date_str = date.strftime("%B %d, %Y")
    file_date = date.strftime("%Y-%m-%d")
    filename = f"{DIGEST_DIR}/{file_date}.md"
    
    # Collect all topics
    all_topics = set()
    for article in articles:
        all_topics.update(article.get("topics", []))
    
    # Build markdown content
    md_content = f"""# 🤖 AI News Digest - {date_str}

> {intro}

*Powered by [Groq](https://groq.com) + [Tavily MCP](https://tavily.com)*

---

## 📊 Today's Coverage

**Articles:** {len(articles)} | **Topics:** {', '.join(sorted(all_topics))}

---

## 📰 Top Stories

"""
    
    # Add each article
    for i, article in enumerate(articles, 1):
        title = article.get("title", "Untitled")
        article_url = article.get("url", "")
        summary = article.get("summary", "No summary available")
        topics = article.get("topics", ["AI"])
        
        topics_badges = " ".join([f"`{t}`" for t in topics])
        
        md_content += f"""### {i}. {title}

{topics_badges}

{summary}

🔗 [Read full article]({article_url})

---

"""
    
    # Add footer
    md_content += f"""
## 📅 Archive

Browse all digests in the [`digests/`](.) folder.

---

*Generated on {date.strftime("%Y-%m-%d at %H:%M UTC")} using Groq + Tavily MCP*
"""
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✓ Digest saved to: {filename}")
    return filename


def update_readme_index(date: datetime):
    """
    Update the digests/README.md with an index of all digests.
    """
    index_file = f"{DIGEST_DIR}/README.md"
    
    # Get list of all digest files
    digest_files = []
    if os.path.exists(DIGEST_DIR):
        for f in os.listdir(DIGEST_DIR):
            if f.endswith('.md') and f != 'README.md':
                digest_files.append(f)
    
    digest_files.sort(reverse=True)  # Most recent first
    
    # Build index content
    index_content = """# 📚 AI News Digest Archive

Daily AI news digests curated by **Groq + Tavily MCP**.

## 📅 All Digests

| Date | Link |
|------|------|
"""
    
    for f in digest_files[:30]:  # Show last 30
        date_str = f.replace('.md', '')
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
            display_date = parsed_date.strftime("%B %d, %Y")
        except ValueError:
            display_date = date_str
        index_content += f"| {display_date} | [{date_str}](./{f}) |\n"
    
    if len(digest_files) > 30:
        index_content += f"\n*...and {len(digest_files) - 30} more in this folder*\n"
    
    index_content += """
---

*Powered by [Groq](https://groq.com) + [Tavily MCP](https://tavily.com)*
"""
    
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"✓ Index updated: {index_file}")


def print_digest_to_console(intro: str, articles: list[dict]):
    """
    Print the digest to console for GitHub Actions logs.
    """
    print("\n" + "=" * 60)
    print("📰 TODAY'S AI NEWS DIGEST")
    print("=" * 60)
    print(f"\n💡 {intro}\n")
    print("-" * 60)
    
    for i, article in enumerate(articles, 1):
        title = article.get("title", "Untitled")
        article_url = article.get("url", "")
        summary = article.get("summary", "")
        topics = article.get("topics", [])
        
        print(f"\n{i}. {title}")
        print(f"   Topics: {', '.join(topics)}")
        print(f"   {summary}")
        print(f"   🔗 {article_url}")
    
    print("\n" + "=" * 60)


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def validate_environment() -> bool:
    """Check that all required environment variables are set."""
    required_vars = [
        ("TAVILY_API_KEY", TAVILY_API_KEY),
        ("GROQ_API_KEY", GROQ_API_KEY),
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
    print(f"   Model: {GROQ_MODEL}")
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
    
    # Step 2: Save as markdown file
    print("\n📝 Step 2: Saving digest...")
    today = datetime.now(timezone.utc)
    
    if not introduction:
        introduction = "Here's your daily roundup of the most important AI and technology news."
    
    # Save to markdown file
    digest_file = save_digest_markdown(today, introduction, articles)
    
    # Update index
    update_readme_index(today)
    
    # Print to console (visible in GitHub Actions logs)
    print_digest_to_console(introduction, articles)
    
    print("\n" + "=" * 60)
    print(f"✅ Daily digest saved to: {digest_file}")
    print("   (Commit will be created by GitHub Actions)")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = run_daily_digest()
    exit(0 if success else 1)
