"""
Loads database configuration from environment variables
This keeps secrets (passwords) out of source control while still
letting every other file simply do `from config import DB_CONFIG`.
"""

import os
from dotenv import load_dotenv

# Reads the .env file in the project and loads it into os.environ
load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "inventory_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}

LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", 10))

