import logging
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
    for topic in TOPICS:
        logger.info(f"Processing: {topic['name']}")
        try:
            result = process_topic(topic)
            if result:
                results.append(result)
                logger.info(f"  Done: {topic['name']}")
            else:
                logger.warning(f"  Skipped (no articles): {topic['name']}")
        except Exception as e:
            logger.error(f"  Error — {topic['name']}: {e}")

    if results:
        logger.info(f"Sending {len(results)} topics to Telegram...")
        send_digest(results)
        logger.info("Digest sent.")
    else:
        logger.error("No results — nothing sent.")


if __name__ == "__main__":
    run_digest()
