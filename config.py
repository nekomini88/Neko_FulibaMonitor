import os

# Telegram Bot Token - set via environment variable TG_BOT_TOKEN
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "")

# Target channel ID for 福利吧监控
TG_CHANNEL_ID = -1004235880182

# Database file path
DB_PATH = "fuliba_monitor.db"

# Fetch interval in seconds (default 60 minutes = 3600 seconds)
FETCH_INTERVAL = 3600

# Sections to monitor (list of URLs)
SECTIONS = [
    "https://fuliba2025.net/%E6%8E%A8%E8%8D%90/",           # 文章推荐
    "https://fuliba2025.net/%E7%BD%91%E7%AB%99%E6%8E%A8%E8%8D%90/", # 网站推荐
    "https://fuliba2025.net/flhz/",                         # 福利汇总
    "https://fuliba2025.net/xiazaizonghezheng/",           # 下载综合症
    "https://fuliba2025.net/tag/%E6%B8%B8%E6%88%8F%E6%8E%A8%E8%8D%90", # 游戏推荐
    "https://fuliba2025.net/dytj/",                        # 电影推荐
    "https://fuliba2025.net/meitusheying/"                 # 美图摄影
]