# 🤖 AI News Daily Digest

Automated content curation system that demonstrates **Groq + Tavily MCP** working together as an agentic system. The AI autonomously searches for news, extracts content, generates summaries, and publishes daily digests to Notion.

**100% Free** - Uses free tiers of Groq, Tavily, Notion API, and GitHub Actions.

## ✨ What Makes This Special: MCP Architecture

This project showcases the power of **Model Context Protocol (MCP)** — instead of making separate API calls, the LLM uses Tavily as an integrated tool:

```
┌─────────────────────────────────────────────────────────────┐
│                    GROQ + TAVILY MCP                        │
│                                                             │
│   ┌─────────────┐    MCP Protocol    ┌─────────────────┐   │
│   │             │◄──────────────────►│                 │   │
│   │  Groq LLM   │    Tool Calls      │  Tavily MCP     │   │
│   │  (compound) │                    │  - tavily_search│   │
│   │             │                    │  - tavily_extract│  │
│   └─────────────┘                    └─────────────────┘   │
│         │                                                   │
│         │ Curated JSON output                              │
│         ▼                                                   │
│   ┌─────────────────────────────────────────────────────┐  │
│   │                    Notion API                        │  │
│   │              (Published Digest)                      │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Key Difference**: The LLM **decides** when and how to use Tavily tools, rather than us orchestrating separate API calls. This is true agentic behavior!

## Features

- 🔗 **MCP Integration**: Groq's Responses API with Tavily MCP tools
- 🤖 **Agentic Workflow**: LLM autonomously searches and curates
- 📰 **Smart Curation**: AI selects and summarizes top 10 stories
- 🏷️ **Auto-Classification**: Topics tagged (LLM, Funding, Startup, etc.)
- 📊 **Notion Database**: Searchable, filterable knowledge base
- ⏰ **Daily Automation**: Runs via GitHub Actions

## Free Tier Usage

| Service | Monthly Limit | Our Usage | Headroom |
|---------|---------------|-----------|----------|
| Tavily | 1,000 credits | ~150 credits | 85% |
| Groq | Rate-limited | ~30 calls | 99% |
| Notion API | Unlimited | ~100 calls | ∞ |
| GitHub Actions | Unlimited (public) | ~90 min | ∞ |

---

## Setup Guide

### Step 1: Get API Keys

#### 1.1 Tavily API Key
1. Go to [app.tavily.com](https://app.tavily.com)
2. Sign up for a free account
3. Copy your API key from the dashboard

#### 1.2 Groq API Key
1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to **API Keys** → Create new key
4. Copy the key (you won't see it again!)

#### 1.3 Notion API Key & Database

##### Create a Notion Integration
1. Go to [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Click **"+ New integration"**
3. Name it: `AI News Digest`
4. Select your workspace
5. Click **Submit**
6. Copy the **Internal Integration Secret** (starts with `secret_`)

##### Create the Notion Database
1. Open Notion and create a new page
2. Add a **Database - Full page**
3. Name it: `AI News Digest`
4. Add these properties (click + to add columns):

| Property Name | Type | Notes |
|---------------|------|-------|
| `Name` | Title | (default, already exists) |
| `Date` | Date | |
| `Top Story` | Text | |
| `Topics` | Multi-select | Add options: `LLM`, `Funding`, `Startup`, `Product Launch`, `Research`, `Regulation`, `Open Source` |
| `Article Count` | Number | |

##### ⚠️ Connect Integration to Database (Important!)
1. Open your database page in Notion
2. Click **⋯** (three dots) in the top right
3. Click **"+ Add connections"**
4. Search for and select `AI News Digest`
5. Click **Confirm**

##### Get Database ID
1. Open your database in Notion
2. Look at the URL: `https://notion.so/your-workspace/DATABASE_ID?v=...`
3. Copy the **DATABASE_ID** part (32 characters, looks like: `a1b2c3d4e5f6...`)

---

### Step 2: Test Locally (Recommended)

Before deploying, test on your machine:

```bash
# Clone your repo
git clone https://github.com/YOUR_USERNAME/ai-news-digest.git
cd ai-news-digest

# Set environment variables
export TAVILY_API_KEY="your-tavily-key"
export GROQ_API_KEY="your-groq-key"
export NOTION_API_KEY="your-notion-secret"
export NOTION_DATABASE_ID="your-database-id"

# Install dependencies
pip install -r requirements.txt

# Run
python daily_digest.py
```

You should see output like:
```
============================================================
🚀 AI News Daily Digest (Groq + Tavily MCP)
   2026-01-21 10:30
============================================================
✓ All environment variables configured

📡 Step 1: Searching and curating AI news via MCP...
🤖 Using Groq + Tavily MCP to search and curate news...
✓ Curated 10 articles
✓ Topics covered: LLM, Funding, Startup, Product Launch

📤 Step 2: Publishing to Notion...
✓ Notion digest created: https://notion.so/...

============================================================
✅ Daily digest published successfully!
============================================================
```

---

### Step 3: Deploy to GitHub

#### 3.1 Create Repository
1. Go to [github.com/new](https://github.com/new)
2. Name: `ai-news-digest`
3. Select **Public** (required for free GitHub Actions)
4. Click **Create repository**

#### 3.2 Upload Files
Upload these files to your repository:
- `daily_digest.py`
- `requirements.txt`
- `.github/workflows/daily-digest.yml`
- `.gitignore`
- `.env.example`

#### 3.3 Add Secrets
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** for each:

| Secret Name | Value |
|-------------|-------|
| `TAVILY_API_KEY` | Your Tavily API key |
| `GROQ_API_KEY` | Your Groq API key |
| `NOTION_API_KEY` | Your Notion integration secret |
| `NOTION_DATABASE_ID` | Your Notion database ID |

---

### Step 4: Run & Schedule

#### Manual Test Run
1. Go to your repo → **Actions** tab
2. Click **"Daily AI News Digest"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs

#### Automatic Schedule
The workflow runs automatically at **8:00 AM UTC** daily.

To change the time, edit `.github/workflows/daily-digest.yml`:
```yaml
schedule:
  - cron: '0 8 * * *'  # 8 AM UTC
  # For 9 AM EST: '0 14 * * *'
  # For 6 AM PST: '0 14 * * *'
```

Use [crontab.guru](https://crontab.guru) to help with cron syntax.

---

## How the MCP Magic Works

```python
# The key part - Tavily as an MCP tool
tools = [{
    "type": "mcp",
    "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
    "server_label": "tavily",
    "require_approval": "never",
}]

# Groq's Responses API with MCP
response = requests.post(
    "https://api.groq.com/openai/v1/responses",
    json={
        "model": "compound-beta",
        "input": "Search for AI news and create a digest...",
        "tools": tools,
    }
)
```

The LLM receives access to Tavily tools (`tavily_search`, `tavily_extract`) and **autonomously decides** how to use them based on the task. This is fundamentally different from making separate API calls!

---

## Troubleshooting

### "Notion creation error: 404"
The integration isn't connected to your database:
1. Open your database in Notion
2. Click **⋯** → **"+ Add connections"**
3. Select your `AI News Digest` integration

### "Groq MCP error: 429"
Rate limited. The script includes automatic retries with backoff. If persistent:
- Wait a few minutes and try again
- Check your Groq usage at [console.groq.com](https://console.groq.com)

### "No articles found"
- Tavily may have returned empty results
- Check your Tavily API key is valid
- Try running again (news availability varies)

### JSON parsing errors
The LLM occasionally formats responses incorrectly. The script handles most cases, but if persistent, try running again.

---

## Customization

### Change Search Focus
Edit the prompt in `search_and_curate_news()`:
```python
prompt = f"""...
Use the tavily_search tool to search for:
- Query: "YOUR CUSTOM SEARCH TERMS"
...
```

### Change Number of Articles
```python
MAX_ARTICLES = 10  # Change to 5, 15, etc.
```

### Add Custom Topics
Modify the topic classification in the prompt:
```python
Topics (classify as: LLM, Funding, Startup, Product Launch, Research, Regulation, Open Source, YOUR_NEW_TOPIC)
```

---

## Project Structure

```
ai-news-digest/
├── daily_digest.py          # Main script (Groq + Tavily MCP)
├── requirements.txt         # Python dependencies
├── .github/
│   └── workflows/
│       └── daily-digest.yml # GitHub Actions automation
├── .env.example             # Template for local testing
├── .gitignore               # Keeps secrets safe
└── README.md                # This file
```

---

## Credits

- **Groq**: Ultra-fast LLM inference with MCP support
- **Tavily**: AI-optimized search API with MCP server
- **Notion**: Beautiful database and publishing platform

Built following the [Groq + Tavily MCP documentation](https://console.groq.com/docs/tavily).

---

## License

MIT License - Feel free to modify and use!
