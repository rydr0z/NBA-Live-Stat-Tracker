import time

import pandas as pd
import streamlit as st
from nba_api.stats.endpoints import teamplayerdashboard

from parameters import SeasonParameters


# decoration to only run this once on first run, then get data from cache
@st.cache(allow_output_mutation=True)
def get_team_stats(team_id, date_from=SeasonParameters.START_DATE, date_to=SeasonParameters.END_DATE, last_n_games=0):
    """Given a team_id (ex. '1610612739' = CLE)
    Returns total season stats for each player on team
    df_team (dataframe)"""
    # Get team stats, then create dataframe
    team_player_dash = teamplayerdashboard.TeamPlayerDashboard(
        team_id,
        headers=SeasonParameters.HEADERS,
        timeout=SeasonParameters.TIMEOUT,
        date_from_nullable=date_from,
        date_to_nullable=date_to,
        last_n_games=str(last_n_games)
    )
    time.sleep(SeasonParameters.SLEEP_INTERVAL)
    tpd = team_player_dash.get_dict()
    data = tpd["resultSets"][1]["rowSet"]
    columns = tpd["resultSets"][1]["headers"]
    df_team = pd.DataFrame(data=data, columns=columns)

    # Change certain columns from total for season to an average
    # By diving by the total number of games played in the season
    df_team[SeasonParameters.COLUMNS_TO_AVG] = df_team[
        SeasonParameters.COLUMNS_TO_AVG
    ].div(df_team["GP"].values, axis=0)

    # Drop unnecessary stats and change column name for joining with daily stats
    df_team.drop(columns=SeasonParameters.COLUMNS_TO_DROP, inplace=True)
    df_team.rename(columns={"PLAYER_NAME": "NAME"}, inplace=True)

    return df_team


def get_season_stats(todays_games, last_n_games=0):
    """Given todays_games (dataframe) get player season stats for each team
    Returns: season_stats_df (dataframe)"""
    # initilize list for storing stats
    team_stats = []
    # loop through today's games, get stats for each away and home team
    # create additional columns for matching with daily stats
    for i, row in todays_games.iterrows():
        away_df = get_team_stats(row["away_id"], last_n_games=last_n_games)
        away_df["team"] = row["away_team"]
        away_df["opp"] = row["home_team"]
        away_df["game_id"] = row["game_id"]
        away_df["awayorhome"] = "away"

        home_df = get_team_stats(row["home_id"])
        home_df["team"] = row["home_team"]
        home_df["opp"] = row["away_team"]
        home_df["game_id"] = row["game_id"]
        home_df["awayorhome"] = "home"

        # store all stats in list
        team_stats.append(away_df)
        team_stats.append(home_df)

    season_stats_df = pd.concat(team_stats)
    return season_stats_df


def get_stats_since(team_ids, date):
    """"""
    # initilize list for storing stats
    team_stats = []
    # loop through today's games, get stats for each away and home team
    # create additional columns for matching with daily stats
    for i, row in team_ids.iterrows():
        df = get_team_stats(row["TEAM_ID"], date_from=date)
        df["team"] = row["TEAM_ABBREVIATION"]
        df["game_id"] = row["GAME_ID"]

        # store all stats in list
        team_stats.append(df)

    stats_since_df = pd.concat(team_stats)
    return stats_since_df
