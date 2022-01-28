from json import JSONDecodeError
import time
from datetime import datetime, timedelta
import pytz
import streamlit as st
import pandas as pd
from data_fetchers.live.constants import Live
from nba_api.live.nba.endpoints import boxscore


def get_live_stats(todays_games):
    """Given todays_games (dataframe) get live player stats from boxscore
    Returns: daily_stats (dataframe)"""
    # initilize list for storing stats
    daily_stats = []
    now = datetime.now(tz=pytz.timezone("EST"))
    # loop through today's games, get boxscore and create dataframes
    # for away team and home team stats in each game
    for i, row in todays_games.iterrows():
        try:
            box = boxscore.BoxScore(row["game_id"])
            time.sleep(Live.SLEEP_INTERVAL)
            away_df = pd.DataFrame(box.away_team_player_stats.get_dict())
            home_df = pd.DataFrame(box.home_team_player_stats.get_dict())

            # statistics stored as nested dict so pop out those values
            away_df = away_df.join(
                pd.DataFrame((away_df.pop("statistics").values.tolist()))
            )

            home_df = home_df.join(
                pd.DataFrame((home_df.pop("statistics").values.tolist()))
            )

            # store game information to match with season stats
            away_df["game_id"], home_df["game_id"] = row["game_id"], row["game_id"]
            away_df["team"], away_df["opp"] = row["away_team"], row["home_team"]
            home_df["team"], home_df["opp"] = row["home_team"], row["away_team"]
            # store all stats in list
            daily_stats.append(away_df)
            daily_stats.append(home_df)
        except JSONDecodeError:
            print("No live data for games yet.")

    daily_stats_df = pd.DataFrame(Live.EXPECTED_COLUMNS, index=[0])

    if daily_stats:
        for i, ds in enumerate(daily_stats):
            if i == 0:
                daily_stats_df = ds
            else:
                daily_stats_df = daily_stats_df.append(ds)

    return daily_stats_df, now


def clean_live_stats(daily_stats):
    daily_stats.drop(
        columns=Live.COLUMNS_TO_DROP, inplace=True,
    )

    daily_stats.rename(
        columns=Live.COLUMNS_TO_RENAME, inplace=True,
    )
