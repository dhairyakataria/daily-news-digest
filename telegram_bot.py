import requests
import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

TELEGRAM_URL = "https://api.telegram.org/bot{token}/sendMessage"

TOPIC_EMOJI = {
    "World News": "\U0001f30d",
    "Technology": "\U0001f4bb",
    "Sports": "\u26bd",
    "India": "\U0001f1ee\U0001f1f3",
    "Geopolitics": "\U0001f310",
    "Politics": "\U0001f3db\ufe0f",
    "Indian Stock Market": "\U0001f4c8",
    "Global Markets": "\U0001f4b9",
    "AI & Machine Learning": "\U0001f916",
}

MAX_LEN = 4096


def _esc(text):
    """Escape HTML special characters for Telegram HTML mode."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _send(text, parse_mode="HTML"):
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
        time.sleep(0.5)
        return True
    except Exception as e:
        logger.error(f"Telegram send failed: {e}")
        return False


def _format_topic(item):
    """Format a single topic block in HTML."""
    name = item["topic"]
    emoji = TOPIC_EMOJI.get(name, "\U0001f4cc")
    lines = [f"{emoji} <b>{_esc(name)}</b>\n"]
    for story in item["stories"]:
        lines.append(f"\u2022 <b>{_esc(story['headline'])}</b>\n{_esc(story['summary'])}")
    return "\n\n".join(lines)


def send_digest(results):
    """
    Send the full news digest using HTML formatting.
    Packs as many topics as possible into each message to minimise noise.
    """
    if not results:
        return

    now = datetime.now().strftime("%d %b %Y, %I:%M %p")
    total = sum(len(r.get("stories", [])) for r in results if r)

    header = (
        f"\U0001f4f0 <b>Daily News Digest</b>\n"
        f"<i>{now}</i>\n"
        f"<i>{len(results)} topics \u00b7 {total} stories</i>"
    )

    sep = "\n\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\n"

    # Build topic blocks
    blocks = []
    for item in results:
        if item and item.get("stories"):
            blocks.append(_format_topic(item))

    # Greedily pack blocks into messages
    messages = []
    current = header

    for block in blocks:
        candidate = current + sep + block
        if len(candidate) > MAX_LEN:
            # Flush current message if it has content beyond the header
            if current != header:
                messages.append(current)
                current = block
            else:
                # Header + first block already too big; send header alone,
                # then try the block on its own
                messages.append(current)
                if len(block) <= MAX_LEN:
                    current = block
                else:
                    # Single topic too long — split by story
                    _send_long_topic(item)
                    current = ""
        else:
            current = candidate

    if current:
        messages.append(current)

    for msg in messages:
        _send(msg)

    logger.info(f"Sent digest in {len(messages)} message(s)")


def _send_long_topic(item):
    """Fallback: send a topic that exceeds 4096 chars as separate story messages."""
    emoji = TOPIC_EMOJI.get(item["topic"], "\U0001f4cc")
    _send(f"{emoji} <b>{_esc(item['topic'])}</b>")
    for story in item["stories"]:
        _send(f"\u2022 <b>{_esc(story['headline'])}</b>\n\n{_esc(story['summary'])}")
