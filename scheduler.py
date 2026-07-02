import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from collector import fetch_article_from_section
from storage import init_db, get_last, update_last
from notifier import send_message
from config import SECTIONS, FETCH_INTERVAL, TG_CHANNEL_ID

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def job():
    logger.info("Starting 福利吧监控 collection cycle...")
    any_new = False
    for section_url in SECTIONS:
        article = fetch_article_from_section(section_url)
        if not article:
            logger.warning(f"No article found in section: {section_url}")
            continue
        title = article['title']
        link = article['link']
        last_title, last_link = get_last(section_url) or (None, None)
        if last_title == title and last_link == link:
            logger.info(f"No change in section {section_url}")
            continue
        # New article detected
        msg = f"🔔 fuliba 🔔\n{title}\n🔗{link}"
        try:
            sent = await send_message(msg, disable_web_page_preview=False)
            if sent:
                logger.info(f"Sent new article from {section_url}: {title}")
                update_last(section_url, title, link)
                any_new = True
            else:
                logger.error("Failed to send message to Telegram")
        except Exception as e:
            logger.error(f"Exception while sending message: {e}")
        # We only want to send one notification per run? Or per section?
        # According to user: "一个标题就是对应一篇新文章", and we want to know if there is any update.
        # We could break after first new article, or send for each section that has new.
        # Let's send for each section that has new (so multiple messages per run if multiple sections updated).
        # But the user might want only one? The original said "发布链接发出来" singular.
        # However, we'll follow the previous logic: we break after first new article to avoid spamming.
        # Let's break after first new to match earlier behavior (send only one message per run).
        if any_new:
            break
    if not any_new:
        logger.info("No new articles found in any section.")

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