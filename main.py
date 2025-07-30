from dotenv import load_dotenv
import os
import requests
from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from helpers import date_handling
from helpersWNBA import get_live_scores

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
    todays_scheduled_ids = []
    if response.status_code == 200:
        data = response.json()
        games = data.get("games", [])
        for game in games:
            # date handling from the helper.py file
            date_handling(game)
        
        live_scores = get_live_scores()
        return render_template('wnba-home.html', raw_data=data, games=data['games'], live_scores=live_scores)
    else:
        return f"API Error: {response.status_code}"


@app.route('/pwhl')
def pwhl_home():
    # Render PWHL page
    return render_template('pwhl-home.html')