import logging
from telegram import Bot
import asyncio
from config import TG_BOT_TOKEN, TG_CHANNEL_ID

logger = logging.getLogger(__name__)

bot = Bot(token=TG_BOT_TOKEN)

async def send_message(text: str, disable_web_page_preview: bool = False) -> bool:
    """
    Send a message to the Telegram channel.
    Returns True if successful, False otherwise.
    """
    try:
        await bot.send_message(chat_id=TG_CHANNEL_ID,
                               text=text,
                               parse_mode='HTML',
                               disable_web_page_preview=disable_web_page_preview)
        logger.info(f"Message sent to channel {TG_CHANNEL_ID}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        return False