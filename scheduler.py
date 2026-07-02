import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from collector import gather_sources
from storage import init_db, is_seen, save_item
from notifier import send_message
from config import FETCH_INTERVAL, TG_CHANNEL_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def job():
    logger.info("Starting 福利吧监控 collection cycle...")
    try:
        items = gather_sources()
        logger.info(f"Collected {len(items)} raw items from sources.")
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
        return

    # We'll look for the first new item (not seen before) in the order they appear on the page.
    for it in items:
        title = it.get("title", "").strip()
        link = it.get("link", "").strip()
        if not title or not link:
            continue
        if is_seen(title, link):
            continue
        # Found a new item
        if not title:
            title = "未获取到标题"
        pub = it.get("pub_date")
        if hasattr(pub, 'isoformat'):
            pub_iso = pub.isoformat()
        elif isinstance(pub, str):
            pub_iso = pub
        else:
            pub_iso = None
        # Save the item (we can store with a dummy score and summary)
        if save_item(title, link, pub_iso, 0, title):
            # Format the message exactly as requested
            msg = f"🔔 fuliba 🔔\n{title}\n🔗{link}"
            try:
                sent = await send_message(msg, disable_web_page_preview=False)
                if sent:
                    logger.info(f"Sent new item to channel {TG_CHANNEL_ID}: {title}")
                else:
                    logger.error("Failed to send message to Telegram")
            except Exception as e:
                logger.error(f"Exception while sending message: {e}")
            # We only send the first new item we find in this cycle.
            break
        else:
            # This should not happen because we checked is_seen, but just in case.
            continue
    else:
        # This block runs if the loop completed without breaking (i.e., no new items found)
        logger.info("No new items found this round.")

async def main():
    init_db()  # Ensure DB and table exist
    scheduler = AsyncIOScheduler()
    # Schedule job to run immediately and then every FETCH_INTERVAL seconds
    scheduler.add_job(job, 'interval', seconds=FETCH_INTERVAL, next_run_time=datetime.now())
    scheduler.start()
    logger.info(f"Scheduler started. Jobs will run every {FETCH_INTERVAL} seconds.")
    # Keep the event loop running
    try:
        await asyncio.Future()  # run forever
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped by user")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())