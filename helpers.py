import requests
import os
from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def date_handling(iso_date_string):
     # date handing 
    if not iso_date_string:
        return "Date unavailable", "Time unavailable"
    try:
        # Parse as UTC
        dt_utc = datetime.fromisoformat(iso_date_string.replace('Z', '+00:00'))
        #Convert to Central Time
        dt_central = dt_utc.astimezone(ZoneInfo("America/Chicago"))
        #format date
        readable_date = dt_central.strftime("%A, %B %d, %Y, %-I:%M %p")

        # Just the time ()
        readable_game_time = dt_central.strftime("%-I:%M %p")

        return readable_date, readable_game_time

    except (ValueError, ZoneInfoNotFoundError, Exception) as e:
        print(f"Failed to parse date: {iso_date_string}. Reason: {e}")
        return "Date unavailable", "Time unavailable"