from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, date, timedelta
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


def get_league_news(num):
    url = "https://wnba-api.p.rapidapi.com/wnba-news"
    querystring = {"limit":num}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    all_news = []

    if response.status_code == 200:
       data = response.json()
       i = 0
       for entry in data:
           all_news.append({
               "description": entry.get("description"),
               "headline": entry.get("headline"),
               "link": entry.get("link"),
               "image": entry.get("images")[0],
               "index": i,
           })
           i += 1
       return all_news
    else:
        return  f"API Error: {response.status_code}"
    

def get_live_scores():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    today_central =  today.astimezone(ZoneInfo("America/Chicago"))
    year = today_central.strftime("%Y")
    month = today_central.strftime("%m")
    day = today_central.strftime("%d")

    url = "https://wnba-api.p.rapidapi.com/wnbascoreboard"

    querystring = {"year":year,"month":month,"day":day}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()

        game_info = []
        i = 0
        for game in data["events"]:
           competition = game["competitions"][i]
           game_info.append({
               "id": game.get("id"),
               "name": game.get("name"),
               "color": game.get("color"),
               "alt_color": game.get("alternateColor"),
               "home_team": competition["competitors"][0],
               "home_team_name": competition["competitors"][0]["team"]["displayName"],
               "home_score": competition["competitors"][0]["score"],
               "away_team": competition["competitors"][1],
               "away_team_name": competition["competitors"][1]["team"]["displayName"],
               "away_score": competition["competitors"][1]["score"],
           })

        return game_info
    else:
        return  f"API Error: {response.status_code}"


def get_yesterdays_scores():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    today_central = today.astimezone(ZoneInfo("America/Chicago"))

    # set the date to tomorrow's date:
    yesterday =  today_central - timedelta(days=1)
    year = yesterday.strftime("%Y")
    month = yesterday.strftime("%m")
    day = yesterday.strftime("%d") 

    

    url = "https://wnba-api.p.rapidapi.com/wnbascoreboard"

    querystring = {"year":year,"month":month,"day":day}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json()

        game_info = []
        i = 0
        for game in data["events"]:
           competition = game["competitions"][i]
           game_info.append({
               "id": game.get("id"),
               "name": game.get("name"),
               "color": game.get("color"),
               "alt_color": game.get("alternateColor"),
               "home_team": competition["competitors"][0],
               "home_team_name": competition["competitors"][0]["team"]["displayName"],
               "home_score": competition["competitors"][0]["score"],
               "away_team": competition["competitors"][1],
               "away_team_name": competition["competitors"][1]["team"]["displayName"],
               "away_score": competition["competitors"][1]["score"],
           })

        return game_info
    else:
        return  f"API Error: {response.status_code}"
        
