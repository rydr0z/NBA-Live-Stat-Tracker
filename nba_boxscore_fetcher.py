import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st

import sys
sys.path.insert(0, 'nba_api/nba_api/live/nba/endpoints')
import scoreboard
import boxscore

def get_daily_player_data(date=None):
    board = scoreboard.ScoreBoard()
    timezone = pytz.timezone('EST')
    now = datetime.now(tz=pytz.timezone('EST'))

    if date == None:
        games = board.games.get_dict()

        game_date = board.score_board_date

        daily_stats = []
        for i, game in enumerate(games):
            game_id = game['gameId']
            away = game['awayTeam']['teamTricode']
            home = game['homeTeam']['teamTricode']
            away_score = str(game['awayTeam']['score'])
            home_score = str(game['homeTeam']['score'])
            period = str(game['period'])
            game_clock = game['gameClock']
            start = datetime.strptime(
                game['gameTimeUTC'], "%Y-%m-%dT%H:%M:%S%z")
            start = start.astimezone(timezone)

            if start < now:
                box = boxscore.BoxScore(game_id)
                away_df = pd.DataFrame(box.away_team_player_stats.get_dict())
                home_df = pd.DataFrame(box.home_team_player_stats.get_dict())
                away_df_stats = away_df.join(pd.DataFrame(
                    (away_df.pop('statistics').values.tolist())))
                away_df_stats['team'] = away
                away_df_stats['opp'] = home
                away_df_stats['score'] = away_score + "-" + home_score
                if game['gameStatusText'] != "Final":
                    away_df_stats['game_clock'] = "Q" + period + " - " + game_clock
                else:
                    away_df_stats['game_clock'] = "Final"
                home_df_stats = home_df.join(pd.DataFrame(
                    (home_df.pop('statistics').values.tolist())))
                home_df_stats['team'] = home
                home_df_stats['opp'] = away
                home_df_stats['score'] = home_score + "-" + away_score
                if game['gameStatusText'] != "Final":
                    home_df_stats['game_clock'] = "Q" + period + " - " + game_clock
                else:
                    home_df_stats['game_clock'] = "Final"
                daily_stats.append(away_df_stats)
                daily_stats.append(home_df_stats)

        daily_stats_df = pd.concat(daily_stats)
        daily_stats_df['minutes'] = daily_stats_df['minutes'].replace('PT','',regex=True).replace('M',':',regex=True).replace('S','',regex=True)

        return daily_stats_df.reset_index()
