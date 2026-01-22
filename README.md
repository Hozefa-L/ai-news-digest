# AI News Daily Digest

Automated daily curation of AI news powered by **Groq's Responses API** and **Tavily MCP**.

This project demonstrates how to build an autonomous news aggregation pipeline using Large Language Models with tool use (MCP). It searches, filters, and summarizes the most significant AI developments each day—completely hands-off.

**[Browse the Digest Archive →](./digests/)**

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  GitHub Action  │────▶│   Groq + MCP    │────▶│ Markdown Digest │
│  (Daily 8AM EST)│     │  (Search+Curate)│     │   (Auto-commit) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Scheduled Trigger**: GitHub Actions runs the pipeline daily at 8:00 AM EST
2. **Dual Search Strategy**: The LLM uses [Tavily MCP](https://tavily.com) to perform two complementary searches:
   - Industry & product news (launches, funding, acquisitions)
   - Technical & research news (papers, open source, breakthroughs)
3. **AI Curation**: [Groq](https://groq.com) processes ~30 search results and selects the top 10 most newsworthy stories
4. **Output**: A formatted Markdown digest is committed to the repository

### What is MCP?

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) is a standard that allows LLMs to use external tools. In this project, Groq's Responses API connects to Tavily's MCP server, enabling the model to perform real-time web searches as part of its reasoning process.

## Coverage

Each digest includes a mix of:

| Category | Examples |
|----------|----------|
| **Product Launches** | New models, API releases, feature announcements |
| **Research** | Papers from arXiv, lab blogs, benchmark results |
| **Funding & M&A** | Startup rounds, acquisitions, partnerships |
| **Open Source** | Model releases, framework updates, tools |
| **Industry Moves** | Regulation, policy, major hires |

Stories are ranked by newsworthiness—not by company name—ensuring diverse coverage across the AI ecosystem.

## Setup Your Own

### Prerequisites

- Python 3.11+
- [Groq API key](https://console.groq.com/) (free tier works)
- [Tavily API key](https://tavily.com/) (1000 free credits/month)

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-news-digest.git
cd ai-news-digest

# Install dependencies
pip install -r requirements.txt

# Run manually
TAVILY_API_KEY=your_key GROQ_API_KEY=your_key python daily_digest.py
```

### GitHub Actions (Automated)

1. Fork this repository
2. Add repository secrets:
   - `TAVILY_API_KEY`
   - `GROQ_API_KEY`
3. Enable GitHub Actions in your fork
4. The workflow runs daily at 8:00 AM EST, or trigger manually from the Actions tab

## Project Structure

```
ai-news-digest/
├── daily_digest.py          # Main pipeline script
├── digests/                  # Generated markdown digests
│   ├── README.md            # Archive index
│   └── YYYY-MM-DD.md        # Daily digests
├── .github/workflows/
│   └── daily-digest.yml     # GitHub Actions workflow
└── requirements.txt
```

## Cost & Limits

| Service | Free Tier | This Project Uses |
|---------|-----------|-------------------|
| Tavily | 1000 credits/month | ~60 credits/month (2 searches/day) |
| Groq | Rate-limited, generous | 1 API call/day |
| GitHub Actions | 2000 mins/month | ~1 min/day |

## License

MIT
