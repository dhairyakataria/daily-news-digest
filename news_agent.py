"""
Agentic news processing using LangChain.

Flow per topic:
  Phase 1 — Fetch headlines from news APIs → LLM picks top 3-5 stories
  Phase 2 — For each story: DuckDuckGo search → LLM writes 100-150 word summary
"""

import logging
import time
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools import DuckDuckGoSearchRun

from llm_call import llm
from news_apis import fetch_gnews, fetch_thenewsapi, fetch_currents

logger = logging.getLogger(__name__)


def _llm_invoke(chain, params, retries=2, delay=5):
    """Invoke an LLM chain with retries and backoff."""
    for attempt in range(retries + 1):
        try:
            return chain.invoke(params)
        except Exception as e:
            if attempt < retries:
                wait = delay * (attempt + 1)
                logger.warning(f"LLM call failed (attempt {attempt+1}/{retries+1}), retrying in {wait}s: {e}")
                time.sleep(wait)
            else:
                raise


# --- Prompts ---

SELECTION_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a news editor. Given a list of headlines, pick the 4 most important "
        "and newsworthy stories. Return only the selected headlines, one per line. "
        "No numbering, no extra text.",
    ),
    (
        "human",
        "Topic: {topic}\n\nHeadlines:\n{headlines}\n\n"
        "Return the 4 most important headlines, one per line:",
    ),
])

STORY_SUMMARY_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a concise news summarizer. Write a clear, factual brief of 100-150 words "
        "about this specific news story. Cover the key facts and context. "
        "No opinion, no fluff. Start directly with the news content — no preamble.",
    ),
    (
        "human",
        "Story: {headline}\n\n"
        "Additional context:\n{context}\n\n"
        "Summary (100-150 words, start directly):",
    ),
])


# --- Helpers ---

def _format_articles(articles):
    lines = []
    for i, a in enumerate(articles, 1):
        title = a.get("title", "")
        desc = a.get("description", "")
        source = a.get("source", "")
        line = f"{i}. [{source}] {title}"
        if desc:
            line += f"\n   {desc[:160]}"
        lines.append(line)
    return "\n".join(lines)


def _fetch_articles(topic_config):
    """Pull articles from all available APIs for a topic, with fallbacks."""
    articles = []
    gnews_topic = topic_config.get("gnews_topic")
    gnews_country = topic_config.get("gnews_country")
    search_query = topic_config.get("search_query")
    # Short query optimised for GNews search (which breaks on long queries)
    gnews_search_query = topic_config.get("gnews_search_query") or search_query

    # Primary: GNews by topic category
    if gnews_topic:
        articles += fetch_gnews(topic=gnews_topic, country=gnews_country, max_results=6)
        time.sleep(1)

    # Secondary: TheNewsAPI keyword search
    if search_query and len(articles) < 4:
        articles += fetch_thenewsapi(query=search_query, max_results=6)
        time.sleep(1)

    # Tertiary: GNews keyword search (uses short query)
    if gnews_search_query and len(articles) < 4:
        articles += fetch_gnews(query=gnews_search_query, max_results=6)
        time.sleep(1)

    # Last resort: CurrentsAPI (20 req/day — only called if all else fails)
    if search_query and len(articles) < 4:
        articles += fetch_currents(query=search_query, max_results=6)

    # Deduplicate by title
    seen, unique = set(), []
    for a in articles:
        t = a["title"]
        if t and t not in seen:
            seen.add(t)
            unique.append(a)

    return unique[:12]


# --- Main function ---

def process_topic(topic_config):
    """
    Returns {"topic": str, "stories": [{"headline": str, "summary": str}, ...]}
    or None if no articles found.
    """
    topic_name = topic_config["name"]

    # Phase 1: fetch headlines
    articles = _fetch_articles(topic_config)
    if not articles:
        logger.warning(f"No articles found for: {topic_name}")
        return None

    headlines_text = _format_articles(articles)

    # Build a title → description map for fallback context
    desc_map = {a["title"]: a.get("description", "") for a in articles}

    # Phase 1: LLM selects top stories
    selection_chain = SELECTION_PROMPT | llm | StrOutputParser()
    selected_raw = _llm_invoke(selection_chain, {"topic": topic_name, "headlines": headlines_text})
    selected_headlines = [h.strip() for h in selected_raw.strip().splitlines() if h.strip()]
    logger.info(f"  LLM selected {len(selected_headlines)} headlines for {topic_name}")

    # Phase 2: for each selected story, search + summarize individually
    ddg = DuckDuckGoSearchRun()
    summary_chain = STORY_SUMMARY_PROMPT | llm | StrOutputParser()
    stories = []

    for headline in selected_headlines[:5]:  # cap at 5
        # Fallback context: use the article description from the API if DDG fails
        fallback = desc_map.get(headline) or headlines_text
        context = fallback
        try:
            context = ddg.run(f"{headline} latest news")
        except Exception as e:
            logger.warning(f"DDG search failed for '{headline[:50]}': {e}")

        # LLM summarizes this individual story
        time.sleep(2)  # pace LLM calls to stay under rate limits
        summary = _llm_invoke(summary_chain, {"headline": headline, "context": context})
        stories.append({"headline": headline, "summary": summary.strip()})

    return {"topic": topic_name, "stories": stories}
