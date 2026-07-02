import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from collector import gather_sources
from storage import init_db, is_seen, mark_seen
from notifier import send_message
from config import FETCH_INTERVAL, TG_CHANNEL_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def job():
    logger.info("Starting 福利吧监控 collection cycle...")
    try:
        items = gather_sources()
        logger.info(f"Collected {len(items)} raw items from sections.")
    except Exception as e:
        logger.error(f"Error during data collection: {e}")
        return

    for item in items:
        title = item.get("title", "").strip()
        link = item.get("link", "").strip()
        if not title or not link:
            continue
        # Filter out any remaining forum links (should already be filtered in collector)
        if 'member.php' in link or 'mod=logging' in link:
            continue

        if not is_seen(link):
            if not title:
                title = "未获取到标题"
            msg = f"🔔 fuliba 🔔\n{title}\n🔗{link}"
            try:
                sent = await send_message(msg, disable_web_page_preview=False)
                if sent:
                    logger.info(f"Sent new article to channel {TG_CHANNEL_ID}: {title}")
                    mark_seen(link)
                else:
                    logger.error("Failed to send message to Telegram")
            except Exception as e:
                logger.error(f"Exception while sending message: {e}")
            # We only send the first new article we find (in the order of sections and then page order)
            break
    else:
        # This block runs if the loop completed without breaking (i.e., no new articles)
        logger.info("No new articles found in this round.")

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