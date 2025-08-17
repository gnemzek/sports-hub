from dotenv import load_dotenv
import os
import requests
from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from helpers import date_handling
from helpersWNBA import get_league_standings, get_league_news, get_live_scores, get_yesterdays_scores, get_team_info

load_dotenv()
api_key = os.getenv("SPORTS_API_KEY")


app = Flask(__name__)

@app.route('/')
def root():
    today = date.today()
    # Code to show homepage based on month. Typically the PWHL and WNBA don't overlap much, if at all. 
    # Example logic: WNBA season May–September, else PWHL
    if 5 <= today.month <= 9:
        return redirect(url_for('wnba_home'))
    else:
        return redirect(url_for('pwhl_home'))
    
@app.route('/wnba')
def wnba_home():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    today_central =  today.astimezone(ZoneInfo("America/Chicago"))
    year = today_central.strftime("%Y")
    month = today_central.strftime("%m")
    day = today_central.strftime("%d")
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
            todays_games_ids = []
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
                    todays_games_ids.append(game["id"])
                    
        yesterdays_scores = get_yesterdays_scores()            
        live_scores = get_live_scores()
        standings_data = get_league_standings()
        news = get_league_news(5)

        return render_template('wnba-home.html', raw_data=data, games=processed_games, teams=standings_data, news=news, live_scores=live_scores, yesterdays_scores=yesterdays_scores)
    else:
        return f"API Error: {response.status_code}"

@app.route('/wnba/news')
def wnba_news():
    news = get_league_news(30)  

    return render_template('wnba-news.html', news=news) 

@app.route("/teams/<team_id>")
def team_info(team_id):
     team = get_team_info(team_id)

     return render_template('team-info.html', team=team )

@app.route('/pwhl')
def pwhl_home():
    # set the date to today's date:
    today = datetime.now(timezone.utc)
    today_central =  today.astimezone(ZoneInfo("America/Chicago"))
    year = today_central.strftime("%Y")
    month = today_central.strftime("%m")
    day = today_central.strftime("%d")


    #get standings
    url = "https://api-hockey.p.rapidapi.com/standings/"

    querystring = {"league":"261","season":year}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "api-hockey.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        data = response.json()
        team_standings = []

        for entry in data["response"][0]: # Iterate through the list of team entries
            team_details = entry.get("team", {})
            games_stats = entry.get("games", {})

            team_standings.append({
                "position": entry.get("position"),
                "name": team_details.get("name")[:-2],
                "logo": team_details.get("logo"),
                "games_played": games_stats.get("played"),
                "wins": games_stats.get("win", {}).get("total"),
                "losses": games_stats.get("lose", {}).get("total"),
                "points": entry.get("points"),
                "form": entry.get("form")
                # Add more fields as needed (e.g., goals for/against, win_overtime, etc.)
            })
    



    # Render PWHL page
    return render_template('pwhl-home.html', teams=team_standings)