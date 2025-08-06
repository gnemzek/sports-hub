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
       all_teams = []

       for entry in data["standings"]["entries"]:
           team_info = entry["team"]

           games_behind_value = ""
           if "stats" in entry:
                for stat in entry["stats"]:
                    if stat.get("abbreviation") == "GB" or stat.get("name") == "gamesBehind":
                        games_behind_value = stat.get("displayValue")
                        break
           all_teams.append({
                "id": team_info.get("id"),
                "name": team_info.get("displayName"),
                "abbreviation": team_info.get("abbreviation"),
                "logo": team_info.get("logos")[0].get("href") if team_info.get("logos") else "",
                "games_behind": games_behind_value
                })

       return all_teams
    else:
        return  f"API Error: {response.status_code}"
