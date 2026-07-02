import os

# Telegram Bot Token - set via environment variable TG_BOT_TOKEN
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")

# Target channel ID for 福利吧监控
TG_CHANNEL_ID = -1004235880182

# Database file path
DB_PATH = "fuliba_monitor.db"

# Fetch interval in seconds (default 1 hour = 3600 seconds)
FETCH_INTERVAL = 3600