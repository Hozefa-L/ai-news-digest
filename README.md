# 🤖 AI News Daily Digest

Automated content curation system that monitors AI/tech news sources, filters by relevance, extracts key information, generates summaries, and publishes daily digests to Notion.

**100% Free** - Uses free tiers of Tavily, Groq, Notion API, and GitHub Actions.

## Features

- 📡 **Automated Search**: Finds the latest AI/tech news daily
- 📄 **Content Extraction**: Pulls full article content for better summaries
- 🤖 **AI Summarization**: Generates concise summaries using Groq's LLaMA 3.3
- 🏷️ **Smart Tagging**: Auto-classifies articles (LLM, Funding, Startup, etc.)
- 📊 **Notion Database**: Searchable, filterable knowledge base
- ⏰ **Daily Automation**: Runs automatically via GitHub Actions

## Architecture

```
GitHub Actions (Daily Cron)
        │
        ▼
┌───────────────────┐
│  1. SEARCH        │  Tavily API (~2 credits)
│  AI/tech news     │  Last 24 hours, top 15 results
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  2. EXTRACT       │  Tavily API (~2 credits)
│  Full content     │  Top 10 articles
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  3. SUMMARIZE     │  Groq API (free)
│  LLaMA 3.3 70B    │  Per-article summaries + intro
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  4. PUBLISH       │  Notion API (free)
│  Database entry   │  Formatted digest page
└───────────────────┘
```

## Free Tier Usage

| Service | Monthly Limit | Our Usage | Headroom |
|---------|---------------|-----------|----------|
| Tavily | 1,000 credits | ~150 credits | 85% |
| Groq | Rate-limited | ~300 calls | 99% |
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

##### Connect Integration to Database
1. Open your database page in Notion
2. Click **•••** (three dots) in the top right
3. Click **"+ Add connections"**
4. Search for and select `AI News Digest`

##### Get Database ID
1. Open your database in Notion
2. Look at the URL: `https://notion.so/your-workspace/DATABASE_ID?v=...`
3. Copy the **DATABASE_ID** part (32 characters, looks like: `a1b2c3d4e5f6...`)

---

### Step 2: Deploy to GitHub

#### 2.1 Create Repository
1. Go to [github.com/new](https://github.com/new)
2. Name: `ai-news-digest`
3. Select **Public** (required for free GitHub Actions)
4. Click **Create repository**

#### 2.2 Upload Files
Upload these files to your repository:
- `daily_digest.py`
- `requirements.txt`
- `.github/workflows/daily-digest.yml`

Or use Git:
```bash
git clone https://github.com/YOUR_USERNAME/ai-news-digest.git
cd ai-news-digest
# Copy the files here
git add .
git commit -m "Initial commit"
git push
```

#### 2.3 Add Secrets
1. Go to your repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** for each:

| Secret Name | Value |
|-------------|-------|
| `TAVILY_API_KEY` | Your Tavily API key |
| `GROQ_API_KEY` | Your Groq API key |
| `NOTION_API_KEY` | Your Notion integration secret |
| `NOTION_DATABASE_ID` | Your Notion database ID |

---

### Step 3: Test & Run

#### Manual Test Run
1. Go to your repo → **Actions** tab
2. Click **"Daily AI News Digest"** workflow
3. Click **"Run workflow"** → **"Run workflow"**
4. Watch the logs for any errors

#### Automatic Scheduling
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

## Customization

### Change Search Topics
Edit `daily_digest.py`:
```python
SEARCH_QUERY = "AI artificial intelligence LLM startup funding product launch"
```

### Change Number of Articles
```python
MAX_ARTICLES = 10  # Change to 5, 15, etc.
```

### Add/Remove Topic Tags
```python
TOPIC_TAGS = {
    "LLM": ["llm", "language model", ...],
    "Your New Topic": ["keyword1", "keyword2"],
}
```

---

## Troubleshooting

### "Missing environment variables"
- Check that all 4 secrets are added in GitHub repo settings
- Secret names must match exactly (case-sensitive)

### "Notion creation error: 401"
- Your Notion integration secret may be wrong
- The integration may not be connected to the database

### "Notion creation error: 404"
- Database ID is incorrect
- Database may have been deleted

### "Tavily search error"
- API key may be invalid
- You may have exceeded your monthly credit limit

### No new digest appearing
- Check GitHub Actions logs for errors
- Verify the workflow is enabled (Actions → select workflow → Enable)

---

## Local Development

Run locally for testing:

```bash
# Set environment variables
export TAVILY_API_KEY="your-key"
export GROQ_API_KEY="your-key"
export NOTION_API_KEY="your-key"
export NOTION_DATABASE_ID="your-database-id"

# Install dependencies
pip install -r requirements.txt

# Run
python daily_digest.py
```

---

## Cost Breakdown

**Monthly cost: $0**

- Tavily: ~5 credits/day × 30 days = 150 credits (free tier: 1,000)
- Groq: ~11 API calls/day × 30 days = 330 calls (free tier: generous limits)
- Notion: Unlimited API calls on free plan
- GitHub Actions: Free for public repositories

---

## License

MIT License - Feel free to modify and use for your own projects!

---

## Contributing

PRs welcome! Ideas for improvements:
- Email delivery option
- Slack/Discord notifications
- Multiple topic digests
- Sentiment analysis
- Historical trend tracking
