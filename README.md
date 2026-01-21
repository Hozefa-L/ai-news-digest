# 🤖 AI News Daily Digest

Automated content curation system demonstrating **Groq + Tavily MCP** as an agentic system. The AI autonomously searches, curates, summarizes, and publishes daily digests to Notion.

**100% Free** - Uses free tiers of Groq, Tavily, Notion API, and GitHub Actions.

## ✨ MCP Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              GROQ RESPONSES API + TAVILY MCP                │
│                                                             │
│   ┌─────────────┐         MCP          ┌────────────────┐  │
│   │   Groq LLM  │◄───────────────────►│  Tavily MCP    │  │
│   │             │    Tool Calls        │  (hosted)      │  │
│   │  gpt-oss-   │                      │                │  │
│   │    120b     │  tavily_search ────► │  • search      │  │
│   │             │                      │                │  │
│   └─────────────┘                      └────────────────┘  │
│          │                                                  │
│          │ Curated JSON                                    │
│          ▼                                                  │
│   ┌─────────────────────────────────────────────────────┐  │
│   │              Notion REST API                         │  │
│   │           (Creates digest page)                      │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Why Notion Uses REST API (Not MCP)

| Service | Has Hosted MCP? | Our Approach |
|---------|-----------------|--------------| 
| **Tavily** | ✅ Yes (`mcp.tavily.com`) | MCP via Groq |
| **Notion** | ❌ No (local server only) | REST API |

Tavily provides a hosted MCP server. Notion's MCP server must run locally, which doesn't work in GitHub Actions. So we use Notion's REST API for reliable publishing.

---

## Features

- 🔗 **MCP Integration**: Groq's Responses API with Tavily MCP
- 🤖 **Agentic Search**: LLM autonomously uses tavily_search tool
- 📰 **Smart Curation**: AI selects and summarizes top 10 stories
- 🏷️ **Auto-Tagging**: Topics classified automatically
- 📊 **Notion Database**: Searchable knowledge base
- ⏰ **Daily Automation**: Runs via GitHub Actions

---

## Quick Start

### 1. Get API Keys

| Service | Get Key At | Free Tier |
|---------|------------|-----------|
| **Tavily** | [app.tavily.com](https://app.tavily.com) | 1,000 credits/mo |
| **Groq** | [console.groq.com/keys](https://console.groq.com/keys) | Generous limits |
| **Notion** | [notion.so/my-integrations](https://www.notion.so/my-integrations) | Unlimited |

### 2. Set Up Notion Database

1. Create a new **Database - Full page** in Notion
2. Name it: `AI News Digest`
3. Add these columns:

| Column | Type |
|--------|------|
| `Name` | Title (default) |
| `Date` | Date |
| `Top Story` | Text |
| `Topics` | Multi-select |
| `Article Count` | Number |

4. **⚠️ Important**: Connect your integration!
   - Click **⋯** (top-right) → **"+ Add connections"** → Select your integration

5. Get Database ID from URL:
   ```
   https://notion.so/workspace/DATABASE_ID?v=...
                            ^^^^^^^^^^^
   ```

### 3. Test Locally

```bash
# Set environment variables
export TAVILY_API_KEY="your-key"
export GROQ_API_KEY="your-key"  
export NOTION_API_KEY="secret_your-key"
export NOTION_DATABASE_ID="your-database-id"

# Install & run
pip install requests
python daily_digest.py
```

### 4. Deploy to GitHub

1. Create a **public** repo
2. Upload all files
3. Add secrets in **Settings → Secrets → Actions**:
   - `TAVILY_API_KEY`
   - `GROQ_API_KEY`
   - `NOTION_API_KEY`
   - `NOTION_DATABASE_ID`
4. Go to **Actions** → **Run workflow**

---

## How the MCP Magic Works

```python
# Tavily MCP configured as a tool
tools = [{
    "type": "mcp",
    "server_url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
    "server_label": "tavily",
    "require_approval": "never",
}]

# Single call - LLM autonomously uses Tavily tools
response = requests.post(
    "https://api.groq.com/openai/v1/responses",
    json={
        "model": "openai/gpt-oss-120b",  # Supports MCP tools
        "input": "Search for AI news and create a digest...",
        "tools": tools,
    }
)
```

The prompt explicitly instructs the LLM to use `tavily_search` with specific parameters — ensuring reliable MCP tool execution!

---

## Scheduling

Runs daily at **8:00 AM UTC**. To change:

```yaml
# .github/workflows/daily-digest.yml
schedule:
  - cron: '0 8 * * *'   # 8 AM UTC
  - cron: '0 14 * * *'  # 9 AM EST
  - cron: '0 15 * * *'  # 7 AM PST
```

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `404 Notion error` | Connect integration: ⋯ → Add connections |
| `429 Rate limited` | Script auto-retries; wait and try again |
| `424 MCP error` | Retry; check Tavily/Groq status pages |
| `No articles found` | Check Tavily API key; try again later |
| `tool calling not supported` | Using wrong model; must be `openai/gpt-oss-120b` |

---

## Cost (Free!)

| Service | Monthly Limit | Our Usage |
|---------|---------------|-----------|
| Tavily | 1,000 credits | ~150 |
| Groq | Generous | ~30 calls |
| Notion | Unlimited | ~30 |
| GitHub Actions | Unlimited (public) | ~90 min |

---

## Project Files

```
ai-news-digest/
├── daily_digest.py              # Main script
├── requirements.txt             # Dependencies  
├── .github/workflows/
│   └── daily-digest.yml         # Automation
├── .env.example                 # Template
└── README.md
```

---

## Credits

Built with [Groq](https://groq.com) + [Tavily MCP](https://tavily.com) following the [official docs](https://console.groq.com/docs/mcp).

MIT License
