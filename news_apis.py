import logging
import requests
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def _iso_24h_ago_gnews():
    """GNews accepts Z suffix: 2026-03-22T16:00:00Z"""
    dt = datetime.now(timezone.utc) - timedelta(hours=24)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso_24h_ago_thenewsapi():
    """TheNewsAPI does NOT accept Z suffix: 2026-03-22T16:00:00"""
    dt = datetime.now(timezone.utc) - timedelta(hours=24)
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _format_articles(raw_list):
    return [
        {
            "title": a.get("title", "").strip(),
            "description": (a.get("description") or "").strip(),
            "source": a.get("source", ""),
        }
        for a in raw_list
        if a.get("title")
    ]


def fetch_gnews(query=None, topic=None, country=None, max_results=5):
    """
    Fetch from GNews API.
    topic: world | nation | business | technology | sports | science | health
    Pass query for keyword search, topic for top-headlines by category.
    """
    api_key = os.getenv("GNEWS_API_KEY")
    if not api_key:
        return []

    params = {"lang": "en", "max": max_results, "token": api_key}

    if topic:
        url = "https://gnews.io/api/v4/top-headlines"
        params["topic"] = topic
        if country:
            params["country"] = country
    else:
        url = "https://gnews.io/api/v4/search"
        params["q"] = query
        params["from"] = _iso_24h_ago_gnews()

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return _format_articles(
            [{"title": a["title"], "description": a.get("description", ""),
              "source": a.get("source", {}).get("name", "")}
             for a in articles]
        )
    except Exception as e:
        logger.error(f"[GNews] {e}")
        return []


def fetch_thenewsapi(query=None, categories=None, locale=None, max_results=5):
    """
    Fetch from TheNewsAPI.
    categories: comma-separated e.g. 'tech,business'
    locale: country code e.g. 'in'
    """
    api_key = os.getenv("THENEWSAPI_KEY")
    if not api_key:
        return []

    params = {"api_token": api_key, "language": "en", "limit": max_results}

    if query:
        url = "https://api.thenewsapi.com/v1/news/all"
        params["search"] = query
        params["published_after"] = _iso_24h_ago_thenewsapi()
    else:
        url = "https://api.thenewsapi.com/v1/news/top"
        if categories:
            params["categories"] = categories
        if locale:
            params["locale"] = locale

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        articles = resp.json().get("data", [])
        return _format_articles(articles)
    except Exception as e:
        logger.error(f"[TheNewsAPI] {e}")
        return []


def fetch_currents(query=None, category=None, max_results=5):
    """
    Fetch from CurrentsAPI (use sparingly — 20 req/day).
    """
    api_key = os.getenv("CURRENTS_API_KEY")
    if not api_key:
        return []

    params = {"apiKey": api_key, "language": "en"}

    if query:
        url = "https://api.currentsapi.services/v1/search"
        params["keywords"] = query
        params["start_date"] = (
            datetime.now(timezone.utc) - timedelta(hours=24)
        ).strftime("%Y-%m-%dT%H:%M:%SZ")  # RFC 3339
    else:
        url = "https://api.currentsapi.services/v1/latest-news"
        if category:
            params["category"] = category

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        articles = resp.json().get("news", [])[:max_results]
        return _format_articles(
            [{"title": a["title"], "description": a.get("description", ""),
              "source": a.get("author", "")}
             for a in articles]
        )
    except Exception as e:
        logger.error(f"[CurrentsAPI] {e}")
        return []
