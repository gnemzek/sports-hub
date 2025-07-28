from dotenv import load_dotenv
import os
import requests
from flask import Flask, render_template
from datetime import datetime, timezone

load_dotenv
api_key = os.getenv("SPORTS_API_KEY")


app = Flask(__name__)

# scheduled games
def scheduled_games(api_data):
    # today's date in the format the API uses as keys (YYYYMMDD)
    now = datetime.now()
    today_key = now.strftime("%Y%m%d")

    upcoming_games = []
    for date_key, games in api_data.items():
        # Only dates today or later
        if date_key >= today_key:
            for game in games:
                # Check if the game's status is not "Final" (i.e., it's upcoming)
                status = game.get("status", {})
                if status.get("state") in ("pre", "in"):  # "pre" or "in" for scheduled/in-progress
                    upcoming_games.append(game)
    return upcoming_games

@app.route('/')
def home():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    print(today.strftime("%Y-%m-%d"))
    url = "https://wnba-api.p.rapidapi.com/wnbaschedule"
    querystring = {"year": today.strftime("%Y"), "month": today.strftime("%m"), "day": today.strftime("%d")}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
  
    if response.status_code == 200:
        data = response.json()
        upcoming_games = scheduled_games(data)
        return render_template('home.html', raw_data=data, upcoming_games=upcoming_games)
    else:
        return f"API Error: {response.status_code}"