import requests
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"


def _escape(text):
    """Escape Telegram MarkdownV1 special characters in plain text."""
    for char in ["_", "*", "`", "["]:
        text = text.replace(char, f"\\{char}")
    return text


def _send(text, parse_mode="Markdown"):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in .env")
        return False

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(
            TELEGRAM_URL.format(token=token), json=payload, timeout=15
        )
        resp.raise_for_status()
        time.sleep(0.5)  # stay well under Telegram's 30 msg/sec limit
        return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def send_digest(results):
    """
    Send the full news digest.
    Each topic gets its own message with all its individual story summaries.
    """
    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    total_stories = sum(len(r.get("stories", [])) for r in results if r)

    _send(f"*News Digest*\n_{now}_\n\n_{len(results)} topics · {total_stories} stories_")

    for item in results:
        if not item or not item.get("stories"):
            continue

        topic_title = _escape(item["topic"])

        # Build one message per topic
        lines = [f"*{topic_title}*"]
        for story in item["stories"]:
            headline = _escape(story["headline"])
            summary = _escape(story["summary"])
            lines.append(f"\n*{headline}*\n{summary}")

        msg = "\n".join(lines)

        # Telegram limit is 4096 chars — split if needed
        if len(msg) <= 4096:
            _send(msg)
        else:
            # Send topic header first, then each story individually
            _send(f"*{topic_title}*")
            for story in item["stories"]:
                headline = _escape(story["headline"])
                summary = _escape(story["summary"])
                _send(f"*{headline}*\n\n{summary}")

    _send("_End of digest\\._")
