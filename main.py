import json
import logging
import os
import time
from datetime import datetime

from news_agent import process_topic
from telegram_bot import send_digest
from config import TOPICS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def run_digest():
    logger.info("=" * 50)
    logger.info(f"Starting digest — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 50)

    results = []
    for i, topic in enumerate(TOPICS):
        logger.info(f"Processing: {topic['name']} ({i+1}/{len(TOPICS)})")
        try:
            result = process_topic(topic)
            if result:
                results.append(result)
                logger.info(f"  Done: {topic['name']} — {len(result['stories'])} stories")
            else:
                logger.warning(f"  Skipped (no articles): {topic['name']}")
        except Exception as e:
            logger.error(f"  Error — {topic['name']}: {e}")

        # Pace between topics to avoid API rate limits
        if i < len(TOPICS) - 1:
            time.sleep(3)

    if results:
        logger.info(f"Sending {len(results)} topics to Telegram...")
        send_digest(results)
        logger.info("Digest sent.")

        # Save digest for the web frontend
        digest_data = {
            "generated_at": datetime.now().isoformat(),
            "topics": results,
        }
        os.makedirs("public", exist_ok=True)
        with open("public/digest.json", "w", encoding="utf-8") as f:
            json.dump(digest_data, f, ensure_ascii=False, indent=2)
        logger.info("Saved public/digest.json")
    else:
        logger.error("No results — nothing sent.")


if __name__ == "__main__":
    run_digest()
