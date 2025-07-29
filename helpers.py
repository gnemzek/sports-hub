from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

def date_handling(game):
     # date handing 
    iso_date = game.get("scheduled") # e.g., "2025-07-25T19:30:00Z"
    try:
        # Parse as UTC
        dt_utc = datetime.fromisoformat(game["scheduled"].replace('Z', '+00:00'))
        #Convert to Central Time
        dt_central = dt_utc.astimezone(ZoneInfo("America/Chicago"))
        #format date
        game["readable_date"] = dt_central.strftime("%A, %B %d, %Y, %-I:%M %p")
    except Exception as e:
        print(f"Failed to parse date: {iso_date}. Reason: {e}")
        game["readable_date"] = "Date unavailable"