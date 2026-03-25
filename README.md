# Daily News Digest

An automated news aggregation and summarization bot that runs every 12 hours, curates the top stories across 9 topics using an LLM, and delivers concise summaries straight to your Telegram.

## How it works

For each of the 9 configured topics, the system:

1. **Fetches headlines** from up to 3 news APIs (GNews, TheNewsAPI, CurrentsAPI) using a waterfall fallback strategy
2. **Deduplicates** articles and keeps up to 12 unique headlines per topic
3. **LLM selects** the 4 most important stories (Llama 3.3 70B via NVIDIA NIM)
4. **Searches DuckDuckGo** for fresh context on each selected story
5. **LLM summarizes** each story in 100–150 words using the headline + web context
6. **Sends the digest** to a Telegram chat, formatted and split within Telegram's message limits

```
Scheduler (every 12h)
      ↓
 main.py → iterates 9 topics
      ↓
 news_agent.py
   ├── _fetch_articles()  →  GNews / TheNewsAPI / CurrentsAPI
   ├── LLM selection      →  NVIDIA NIM (Llama 3.3 70B)
   ├── DuckDuckGo search  →  fresh context per story
   └── LLM summarization  →  100–150 word summary
      ↓
 telegram_bot.py  →  Telegram Chat
```

## Topics covered

| Topic | Focus |
|---|---|
| World News | Global crises, disasters, wars, summits |
| Technology | Hardware, software, startups, big tech |
| Sports | Cricket, football, tennis, IPL, Premier League |
| India | Economy, infrastructure, employment, society |
| Geopolitics | Country relations, alliances, sanctions, treaties |
| Politics | Indian domestic politics, elections, parliament |
| Indian Stock Market | NSE, BSE, Nifty, Sensex |
| Global Markets | S&P500, Dow, Fed, currencies, commodities |
| AI & Machine Learning | OpenAI, Anthropic, DeepMind and more |

## Stack

- **LLM:** Llama 3.3 70B via [NVIDIA NIM](https://build.nvidia.com) — `langchain-nvidia-ai-endpoints`
- **Orchestration:** LangChain (LCEL chains, `ChatPromptTemplate`, `StrOutputParser`)
- **Web search:** DuckDuckGo via `langchain-community`
- **News sources:** GNews, TheNewsAPI, CurrentsAPI
- **Delivery:** Telegram Bot API
- **Scheduler:** `schedule` library (12-hour intervals)

## API usage per run (2 runs/day)

| API | Free limit/day | Used per run |
|---|---|---|
| GNews | 100 requests | ~20 |
| TheNewsAPI | 100 requests | ~20 |
| CurrentsAPI | 20 requests | ~0 (fallback only) |
| DuckDuckGo | Unlimited | ~18 |
| NVIDIA NIM (Llama 3.3 70B) | Varies | ~45 LLM calls |
| Telegram | 30 msg/sec | ~30–50 messages |

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/dhairyakataria/daily-news-digest.git
cd daily-news-digest
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the example file and fill in your API keys:

```bash
cp .env.example .env
```

| Variable | Where to get it |
|---|---|
| `NVIDIA_API_KEY` | [build.nvidia.com](https://build.nvidia.com) |
| `GNEWS_API_KEY` | [gnews.io/dashboard](https://gnews.io/dashboard) |
| `THENEWSAPI_KEY` | [thenewsapi.com/account/dashboard](https://www.thenewsapi.com/account/dashboard) |
| `CURRENTS_API_KEY` | [currentsapi.services/en/profile](https://currentsapi.services/en/profile) |
| `TELEGRAM_BOT_TOKEN` | From `@BotFather` on Telegram |
| `TELEGRAM_CHAT_ID` | Your personal chat ID (see below) |

### 4. Set up Telegram

**Create a bot:**
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the token you receive — that's your `TELEGRAM_BOT_TOKEN`

**Get your Chat ID:**
1. Send any message to your new bot
2. Open `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates` in your browser
3. Find `"chat":{"id": XXXXXXXXX}` — that number is your `TELEGRAM_CHAT_ID`

### 5. Run

```bash
python main.py
```

The script runs immediately on startup, then repeats every 12 hours. Logs are written to `digest.log`.

Press `Ctrl+C` to stop.

## Project structure

```
daily-news-digest/
├── main.py          # Entry point and scheduler
├── news_agent.py    # Core agentic logic (fetch → select → summarize)
├── news_apis.py     # GNews, TheNewsAPI, CurrentsAPI integrations
├── llm_call.py      # NVIDIA NIM LLM initialization
├── telegram_bot.py  # Telegram formatting and delivery
├── config.py        # Topic definitions and search queries
├── requirements.txt
└── .env.example
```
