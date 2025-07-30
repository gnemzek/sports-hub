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

def get_league_standings():
    url = "https://api.sportradar.com/wnba/trial/v8/en/seasons/2025/REG/standings.json"

    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        standings = {
            'eastern': [],
            'western': [],
            'league': [],
            'season_info': {
                'year': data.get('season', {}).get('year'),
                'type': data.get('season', {}).get('type')
            }
        }

        all_teams = []
        
        for conference in data.get('conferences', []):
            conf_name = conference.get('name', '').lower()
            teams_data = []
            
            for team in conference.get('teams', []):
                team_info = {
                    'conf_name': conf_name,
                    'team_name': f"{team.get('market', '')} {team.get('name', '')}".strip(),
                    'wins': team.get('wins', 0),
                    'losses': team.get('losses', 0),
                    'win_pct': team.get('win_pct', 0),
                    'games_behind': team.get('games_behind', {}).get('conference', 0),
                    'streak': f"{team.get('streak', {}).get('kind', '').title()} {team.get('streak', {}).get('length', 0)}",
                    'conf_rank': team.get('calc_rank', {}).get('conf_rank', 0),
                    'league_rank': team.get('calc_rank', {}).get('league_rank', 0),
                    'points_for': team.get('points_for', 0),
                    'points_against': team.get('points_against', 0),
                    'point_diff': team.get('point_diff', 0)
                }

                # make the conference name look better for front-end
                if team_info['conf_name'] == "western conference":
                    team_info['pretty_conf_name'] = "Western"
                elif team_info['conf_name'] == "eastern conference":
                    team_info['pretty_conf_name'] = "Eastern"
                teams_data.append(team_info)
                all_teams.append(team_info)
            
            # Sort by conference rank
            teams_data.sort(key=lambda x: x['conf_rank'])
            
            if 'eastern' in conf_name:
                standings['eastern'] = teams_data
            elif 'western' in conf_name:
                standings['western'] = teams_data

        # Sort all teams by league rank for combined standings
        all_teams.sort(key=lambda x: x['league_rank'])
        standings['league'] = all_teams
        
        return standings
    else:
        return {'eastern': [], 'western': [], 'error': f"API Error: {response.status_code}"}

