from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
import time
from helpers import date_handling

load_dotenv()
api_key = os.getenv("SPORTS_API_KEY")

def get_live_scores():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    live_scores = []
    todays_scheduled_ids = []

    # get todays schedule
    url = f"https://api.sportradar.com/wnba/trial/v8/en/games/{year}/{month}/{day}/schedule.json"
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }
    response = requests.get(url, headers=headers)
    

    if response.status_code == 200:
        data = response.json()
        games = data.get("games", [])
        for game in games:
            # add daily schedule game ids to list to grab for Live Scores
            todays_scheduled_ids.append(game["id"])
        
        for game_id in todays_scheduled_ids:
            url_for_game = f"https://api.sportradar.com/wnba/trial/v8/en/games/{game_id}/boxscore.json"
            headers = {
                "accept": "application/json",
                "x-api-key": api_key
            }
            scores_response = requests.get(url_for_game, headers=headers)
            print(f"Status code: {scores_response.status_code}")
            scores_data = scores_response.json()
            if scores_response.status_code == 200:
                game_info = {
                    'game_id': game_id,
                    'status': scores_data.get('status'),
                    'home_team': f"{scores_data.get('home', {}).get('market', '')} {scores_data.get('home', {}).get('name', '')}",
                    'home_score': scores_data.get('home', {}).get('points', 0),
                    'home_alias': scores_data.get('home', {}).get('alias', ''),
                    'away_team': f"{scores_data.get('away', {}).get('market', '')} {scores_data.get('away', {}).get('name', '')}",
                    'away_score': scores_data.get('away', {}).get('points', 0),
                    'away_alias': scores_data.get('away', {}).get('alias', ''),
                    'scheduled': scores_data.get('scheduled'),
                }
                if game_info["status"] == "created":
                    game_info["status"] = "Scheduled"
                date_handling(game_info)
                live_scores.append(game_info)
            elif scores_response.status_code == 429:
                print("Rate limited! Waiting...")
                time.sleep(2)  # Wait 2 seconds before continuing
            elif scores_response.status_code == 404:
                print(f"Boxscore not found for game {game_id}")
        return live_scores
    else:
        return f"API Error: {response.status_code}", []


