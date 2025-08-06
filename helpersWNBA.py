from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
import time
from helpers import date_handling

load_dotenv()
api_key = os.getenv("SPORTS_API_KEY")


def get_league_standings():
    url = "https://wnba-api.p.rapidapi.com/wnbastandings"
    today = datetime.now(timezone.utc)
    year = today.strftime("%Y")

    querystring = {"year":year}

    headers = {
	"x-rapidapi-key": api_key,
	"x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
       data = response.json()
       print("testing...")
       all_teams = []

       for entry in data["standings"]["entries"]:
           team_info = entry["team"]
           all_teams.append(team_info)

       return all_teams
    else:
        return  f"API Error: {response.status_code}"
