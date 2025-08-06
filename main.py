from dotenv import load_dotenv
import os
import requests
from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from helpers import date_handling
from helpersWNBA import get_live_scores, get_league_standings

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
    todays_id = year + month + day

    # get todays schedule
    url = f"https://wnba-api.p.rapidapi.com/wnbaschedule"

    querystring = {"year":year,"month":month,"day":day}
    headers = {
	"x-rapidapi-key": api_key,
	"x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        
        if todays_id in data:
            processed_games = []
            todays_games = data[todays_id]
            for game in todays_games:
                home_team = None
                away_team = None
                for competitor in game.get('competitors', []):
                    if competitor.get('isHome'):
                        home_team = competitor
                    else:
                        away_team = competitor
                if home_team and away_team:
                    # date handling from the helper.py file
                    readable_date, readable_game_time = date_handling(game.get("date"))
                    print(readable_game_time)
                    processed_games.append({
                        "id": game["id"],
                        "home_team": home_team["displayName"],
                        "away_team": away_team["displayName"],
                        "home_score": home_team.get("score"),
                        "away_score": away_team.get("score"),
                        "winner": home_team["displayName"] if home_team.get("winner") else away_team["displayName"] if away_team.get("winner") else "N/A",
                        "completed": game["completed"],
                        "readable_date": readable_date,
                        "readable_time": readable_game_time
                    })
                    
        
            
        return render_template('wnba-home.html', raw_data=data, games=processed_games)
    else:
        return f"API Error: {response.status_code}"


@app.route('/pwhl')
def pwhl_home():
    # Render PWHL page
    return render_template('pwhl-home.html')