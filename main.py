from dotenv import load_dotenv
import os
import requests
from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from helpers import date_handling

load_dotenv()
api_key = os.getenv("SPORTS_API_KEY")


app = Flask(__name__)

@app.route('/')
def root():
    today = date.today()
    # Example logic: WNBA season May–September, else PWHL
    if 5 <= today.month <= 9:
        return redirect(url_for('wnba_home'))
    else:
        return redirect(url_for('pwhl_home'))
    
@app.route('/wnba')
def wnba_home():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

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
            date_handling(game)
            home_team = game["home"]["name"]
            away_team = game["away"]["name"]
            tip_time = game["readable_date"]
            venue = game["venue"]["name"]
            city = game["venue"]["city"]
        return render_template('wnba-home.html', raw_data=data, games=data['games'])
    else:
        return f"API Error: {response.status_code}"


@app.route('/pwhl')
def pwhl_home():
    # Render PWHL page
    return render_template('pwhl-home.html')