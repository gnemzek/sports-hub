from dotenv import load_dotenv
import os
import requests
from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo
import time
from helpers import date_handling
import random

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
                for stat in entry["stats"]:
                    if stat.get("name") == "League Standings":
                        league_standing = stat.get("summary")
                        break
           all_teams.append({
                "id": team_info.get("id"),
                "name": team_info.get("displayName"),
                "abbreviation": team_info.get("abbreviation"),
                "logo": team_info.get("logos")[0].get("href") if team_info.get("logos") else "",
                "games_behind": games_behind_value,
                "record": league_standing
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
           game_id = game.get("id")
           # print(game_id)
           game_info.append({
               "id": game_id,
               "name": game.get("name"),
               "color": game.get("color"),
               "alt_color": game.get("alternateColor"),
               "home_team": competition["competitors"][0],
               "home_team_name": competition["competitors"][0]["team"]["displayName"],
               "home_score": competition["competitors"][0]["score"],
               "away_team": competition["competitors"][1],
               "away_team_name": competition["competitors"][1]["team"]["displayName"],
               "away_score": competition["competitors"][1]["score"],
               "status": competition["status"]["type"]["description"]
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
            game_id = game.get("id")
            # print(game_id)
            game_info_dict = {
               "id": game_id,
               "name": game.get("name"),
               "color": game.get("color"),
               "alt_color": game.get("alternateColor"),
               "home_team": competition["competitors"][0],
               "home_team_name": competition["competitors"][0]["team"]["displayName"],
               "home_score": competition["competitors"][0]["score"],
               "away_team": competition["competitors"][1],
               "away_team_name": competition["competitors"][1]["team"]["displayName"],
               "away_score": competition["competitors"][1]["score"],
            }

            game_summary_info = get_game_summary(game_id)
            game_summary_dict = {
                "link": game_summary_info["seasonSeries"][0]["events"][2]["links"][0]["href"],
                "away_short_display": game_summary_info["boxScore"]["teams"][0]["team"]["shortDisplayName"],
                "home_short_display": game_summary_info["boxScore"]["teams"][1]["team"]["shortDisplayName"],
                "away_team_color": game_summary_info["boxScore"]["teams"][0]["team"]["color"],
                "home_team_color": game_summary_info["boxScore"]["teams"][1]["team"]["color"],
                "away_FG_score": game_summary_info["boxScore"]["teams"][0]["statistics"][0]["displayValue"],
                "home_FG_score": game_summary_info["boxScore"]["teams"][1]["statistics"][0]["displayValue"],
                "away_FG_percentage": game_summary_info["boxScore"]["teams"][0]["statistics"][1]["displayValue"],
                "home_FG_percentage": game_summary_info["boxScore"]["teams"][1]["statistics"][1]["displayValue"],
                "away_3PT_score": game_summary_info["boxScore"]["teams"][0]["statistics"][2]["displayValue"],
                "home_3PT_score": game_summary_info["boxScore"]["teams"][1]["statistics"][2]["displayValue"],
                "away_3PT_percentage": game_summary_info["boxScore"]["teams"][0]["statistics"][3]["displayValue"],
                "home_3PT_percentage": game_summary_info["boxScore"]["teams"][1]["statistics"][3]["displayValue"],
                "away_freeThrow_score": game_summary_info["boxScore"]["teams"][0]["statistics"][4]["displayValue"],
                "home_freeThrow_score": game_summary_info["boxScore"]["teams"][1]["statistics"][4]["displayValue"],
                "away_freeThrow_percentage": game_summary_info["boxScore"]["teams"][0]["statistics"][5]["displayValue"],
                "home_freeThrow_percentage": game_summary_info["boxScore"]["teams"][1]["statistics"][5]["displayValue"],
                "away_total_rebounds": game_summary_info["boxScore"]["teams"][0]["statistics"][6]["displayValue"],
                "home_total_rebounds": game_summary_info["boxScore"]["teams"][1]["statistics"][6]["displayValue"],
                "away_offensive_rebounds": game_summary_info["boxScore"]["teams"][0]["statistics"][7]["displayValue"],
                "home_offensive_rebounds": game_summary_info["boxScore"]["teams"][1]["statistics"][7]["displayValue"],
                "away_defensive_rebounds": game_summary_info["boxScore"]["teams"][0]["statistics"][8]["displayValue"],
                "home_defensive_rebounds": game_summary_info["boxScore"]["teams"][1]["statistics"][8]["displayValue"],
                "away_assists": game_summary_info["boxScore"]["teams"][0]["statistics"][9]["displayValue"],
                "home_assists": game_summary_info["boxScore"]["teams"][1]["statistics"][9]["displayValue"],
                "away_steals": game_summary_info["boxScore"]["teams"][0]["statistics"][10]["displayValue"],
                "home_steals": game_summary_info["boxScore"]["teams"][1]["statistics"][10]["displayValue"],
                "away_blocks": game_summary_info["boxScore"]["teams"][0]["statistics"][11]["displayValue"],
                "home_blocks": game_summary_info["boxScore"]["teams"][1]["statistics"][11]["displayValue"],
                "away_turnovers": game_summary_info["boxScore"]["teams"][0]["statistics"][12]["displayValue"],
                "home_turnovers": game_summary_info["boxScore"]["teams"][1]["statistics"][12]["displayValue"],
            }

            combined_dicts = game_info_dict | game_summary_dict

            game_info.append(combined_dicts)
            

        return game_info
    else:
        return  f"API Error: {response.status_code}"
    

def get_game_summary(game_id):
    summary_url = "https://wnba-api.p.rapidapi.com/wnbasummary"
    summary_querystring = {"gameId":game_id}

    summary_headers = {
                "x-rapidapi-key": api_key,
                "x-rapidapi-host": "wnba-api.p.rapidapi.com"
        }
           
    summary_response = requests.get(summary_url, headers=summary_headers, params=summary_querystring)

    game_summary_info = {}

    if summary_response.status_code == 200:
        summary_data = summary_response.json()
        
        game_summary_info.update(summary_data)

        return game_summary_info

    else:
        return  f"API Error: {summary_response.status_code}"

        
def get_team_info(team_id):

    url = "https://wnba-api.p.rapidapi.com/wnbateaminfo"

    querystring = {"teamid":team_id}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    team_info = []

    if response.status_code == 200:
        data = response.json()

        team_info.append({
            "name": data["team"]["displayName"],
            "color": data["team"]["color"],
            "alternateColor": data["team"]["alternateColor"],
            "logo": data["team"]["logos"][0]["href"],
            "record": data["team"]["record"]["items"][0]["summary"],
            "link": data["team"]["links"][0]["href"],
            "standings": data["team"]["standingSummary"],
            "overallRecord": data["team"]["record"]["items"][0]["summary"],
        })
          

        return team_info
    
    else:
        return  f"API Error: {response.status_code}"

def get_team_roster(team_id):
    
    url = "https://wnba-api.p.rapidapi.com/team-roster"

    querystring = {"teamId":team_id}

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    team_roster = []

    if response.status_code == 200:
        data = response.json()

        for player in data["data"]:

            team_roster.append({
                "player_id": player["playerId"],
                "fullname": player["fullName"],
                "age": player["age"],
                "headshot": player["headshot"],
                "number": player["jersey"],

            })
       
          

        return team_roster
    
    else:
        return  f"API Error: {response.status_code}"


def get_team_ids():
    url = "https://wnba-api.p.rapidapi.com/team/id"

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    team_ids = []

    if response.status_code == 200:
        data = response.json()

        i = 0

        for team in data:
            team_ids.append(
                data[i]["teamId"]
            )
            i += 1
          

        return team_ids
    
    else:
        return  f"API Error: {response.status_code}"

def get_team_players():
    team_ids = get_team_ids()

    random_team_id = random.choice(team_ids)
    
    roster_url = "https://wnba-api.p.rapidapi.com/team-roster"

    roster_querystring = {"teamId": random_team_id}

    roster_headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    roster_response = requests.get(roster_url, headers=roster_headers, params=roster_querystring)

    players = []


    if roster_response.status_code == 200:
        data = roster_response.json()
        
        for player in data["data"]:

            players.append({
                "id":player["playerId"],
                "name": player["fullName"],
                "headshot": player["headshot"]
            })


          
        return players
        
    
    else:
        return  f"API Error: {roster_response.status_code}"

def get_random_player():
    today = datetime.now(timezone.utc)
    year = today.strftime("%Y")
    players = get_team_players()


    random_player = random.choice(players)

    player_stats = []

    url = "https://wnba-api.p.rapidapi.com/player-overview"

    querystring = {"playerId":random_player["id"]}


    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "wnba-api.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    
    if response.status_code == 200:
        data = response.json()

        player_stats.append({
            "id": random_player["id"],
            "name": random_player["name"],
            "headshot": random_player.get("headshot", "../static/placeholder.jpg"),
            "PPG": data["player_overview"]["statistics"]["splits"][0]["stats"][2],
            "APG": data["player_overview"]["statistics"]["splits"][0]["stats"][4],
            "TPP": data["player_overview"]["statistics"]["splits"][0]["stats"][9],
            "FGP": data["player_overview"]["statistics"]["splits"][0]["stats"][10]
        })
      
        print(player_stats)
        return player_stats
    
    else:
        return  f"API Error: {response.status_code}"




