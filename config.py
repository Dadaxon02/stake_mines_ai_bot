"""
STAKE MINES AI - Configuration Manager
Loads environment variables securely
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID = os.getenv("ADMIN_ID", "0").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "stake_mines.db")
WEBAPP_URL = os.getenv("WEBAPP_URL", "")

if not BOT_TOKEN:
    print("\n" + "=" * 60)
    print("OGOHLANTIRISH: BOT_TOKEN topilmadi!")
    print("1. @BotFather orqali yangi bot yarating va tokenni oling.")
    print("2. .env fayliga quyidagicha yozing: BOT_TOKEN=sizning_tokeningiz")
    print("=" * 60 + "\n")
