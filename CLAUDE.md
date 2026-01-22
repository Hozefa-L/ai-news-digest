# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI News Daily Digest is an automated news curation system that generates daily AI news summaries. It uses Groq's Responses API with Tavily MCP (Model Context Protocol) for real-time web search and content extraction.

## Commands

### Run the digest locally
```bash
TAVILY_API_KEY=<key> GROQ_API_KEY=<key> python daily_digest.py
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Architecture

**Single-file Python application** (`daily_digest.py`) with this flow:
1. `groq_with_tavily_mcp()` - Calls Groq's `/openai/v1/responses` endpoint with Tavily MCP configured as a tool
2. `search_and_curate_news()` - Uses dual-search strategy (industry news + technical/research news) for diverse coverage
3. `save_digest_markdown()` - Writes curated articles to `digests/YYYY-MM-DD.md`
4. `update_readme_index()` - Updates `digests/README.md` with links to all digests

**Key configuration** (in `daily_digest.py`):
- `GROQ_MODEL = "openai/gpt-oss-120b"` - Model supporting MCP tools
- `MAX_ARTICLES = 10` - Number of articles per digest
- Uses EST timezone (UTC-5) for digest dates
- Tavily credits: 2 basic searches/day (~60/month, budget is 1000)

**GitHub Actions** (`.github/workflows/daily-digest.yml`):
- Runs daily at 8:00 AM EST (13:00 UTC)
- Requires `TAVILY_API_KEY` and `GROQ_API_KEY` as repository secrets
- Auto-commits generated digests to the `digests/` folder

## Output

Digests are markdown files in `digests/` with:
- Introduction summarizing the day's top AI development
- Curated articles with title, summary, topics, source, and URL
- Coverage table showing topics and sources
