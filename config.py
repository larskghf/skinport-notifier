import os
from dotenv import load_dotenv
from typing import Dict, Union, List

load_dotenv()

# Skinport API Configuration
SKINPORT_API_URL = "https://api.skinport.com/v1"
SKINPORT_API_KEY = os.getenv("SKINPORT_API_KEY")
SKINPORT_API_SECRET = os.getenv("SKINPORT_API_SECRET")

# Discord Webhook Configuration
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Items to monitor with optional price thresholds
# If price_threshold is set, only notify on price drops below threshold
# If price_threshold is None, notify on both quantity increases and any price drops
TARGET_ITEMS: Dict[str, Union[float, None]] = {
    "★ Falchion Knife | Gamma Doppler (Factory New)": 350.00,  # Alert when price drops below 350€
    "M4A4 | Etch Lord (Minimal Wear)": None,  # Monitor both quantity and price
    "Kilowatt Case": 1.50,  # Alert when price drops below 1.50€
    "Chroma 2 Case": None,  # Monitor both quantity and price
    "Operation Breakout Weapon Case": 3.00,  # Alert when price drops below 3€
    "Gallery Case": None  # Monitor both quantity and price
}

# Check interval in minutes (increased to avoid rate limiting)
CHECK_INTERVAL = 5

# Rate limit handling
RATE_LIMIT_DELAY = 60 * 60  # 60 minutes in seconds