# 🤖 AI News Daily Digest

Automated AI news curation using **Groq + Tavily MCP**. The AI autonomously searches, curates, and summarizes daily digests — saved as Markdown files right in this repo!

**100% Free** - Uses free tiers of Groq, Tavily, and GitHub Actions.

## ✨ How It Works

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
│          │ Curated Articles                                │
│          ▼                                                  │
│   ┌─────────────────────────────────────────────────────┐  │
│   │            Markdown File (digests/)                  │  │
│   │         Committed to GitHub Repo                     │  │
│   └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📚 View Digests

Browse all AI news digests in the **[`digests/`](./digests/)** folder!

---

## Features

- 🔗 **MCP Integration**: Groq's Responses API with Tavily MCP
- 🤖 **Agentic Search**: LLM autonomously uses `tavily_search` tool
- 📰 **Smart Curation**: AI selects and summarizes top 10 stories
- 🏷️ **Auto-Tagging**: Topics classified automatically
- � **Git Archive**: All digests saved as searchable Markdown
- ⏰ **Daily Automation**: Runs via GitHub Actions

---

## Quick Start

### 1. Get API Keys (2 keys only!)

| Service | Get Key At | Free Tier |
|---------|------------|-----------|
| **Tavily** | [app.tavily.com](https://app.tavily.com) | 1,000 credits/mo |
| **Groq** | [console.groq.com/keys](https://console.groq.com/keys) | Generous limits |

### 2. Deploy to GitHub

1. Fork or create a **public** repo
2. Upload all files
3. Add secrets in **Settings → Secrets → Actions**:
   - `TAVILY_API_KEY`
   - `GROQ_API_KEY`
4. Go to **Actions** → **Run workflow**

That's it! The digest will be saved to `digests/YYYY-MM-DD.md` and auto-committed.

### 3. Test Locally (Optional)

```bash
# Set environment variables
export TAVILY_API_KEY="your-key"
export GROQ_API_KEY="your-key"

# Install & run
pip install requests
python daily_digest.py

# Check the output
cat digests/$(date +%Y-%m-%d).md
```

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

# Single call - LLM autonomously uses Tavily search
response = requests.post(
    "https://api.groq.com/openai/v1/responses",
    json={
        "model": "openai/gpt-oss-120b",
        "input": "Use tavily_search to find AI news...",
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

## Project Structure

```
ai-news-digest/
├── daily_digest.py              # Main script
├── requirements.txt             # Dependencies  
├── digests/                     # 📚 All digests saved here!
│   ├── README.md               # Auto-generated index
│   ├── 2024-01-21.md
│   ├── 2024-01-20.md
│   └── ...
├── .github/workflows/
│   └── daily-digest.yml         # Automation
└── README.md
```

---

## Cost (Free!)

| Service | Monthly Limit | Our Usage |
|---------|---------------|-----------|
| Tavily | 1,000 credits | ~150 |
| Groq | Generous | ~30 calls |
| GitHub Actions | Unlimited (public) | ~90 min |

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `429 Rate limited` | Script auto-retries; wait and try again |
| `424 MCP error` | Retry; check Tavily/Groq status pages |
| `No articles found` | Check Tavily API key; try again later |
| `Permission denied` | Ensure workflow has `contents: write` permission |

---

## Credits

Built with [Groq](https://groq.com) + [Tavily MCP](https://tavily.com) following the [official docs](https://console.groq.com/docs/mcp).

MIT License
