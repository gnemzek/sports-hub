from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
import time
from helpers import date_handling

load_dotenv()
api_key = os.getenv("SPORTS_API_KEY")

