import pandas as pd
import streamlit as st
from data_combine.constants import Combined


def combine_data(todays_games, daily_stats_df, season_stats_df, topshot_data):
    """This is the function for combining the data fetched from various sources"""
    daily_stats_df.set_index(["name", "team", "opp"], inplace=True)
    season_stats_df.set_index(["name", "team", "opp"], inplace=True)
    stats_df = season_stats_df.join(
        daily_stats_df, on=["name", "team", "opp"], lsuffix="_avg", rsuffix="",
    )
    stats_df.reset_index(inplace=True)
    stats_df["game_id"] = stats_df["game_id_avg"]

    stats_df.set_index("name", inplace=True)
    stats_df = stats_df.join(topshot_data, on="name", lsuffix="_nba", rsuffix="_TS")
    stats_df.reset_index(inplace=True)
    stats_df.set_index("game_id", inplace=True)
    todays_games.set_index("game_id", inplace=True)
    stats_df = stats_df.join(todays_games, on="game_id")

    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"team_nba": "team"}, inplace=True)
    stats_df.set_index(["name", "team", "opp"], inplace=True)
    return stats_df


def time_to_float(df):
    # format player minutes to be more readable
    df["min"] = df["min"].fillna("PT00M00.00S")
    time = (
        df["min"]
        .str.replace("PT", "", regex=True)
        .str.replace("S", "", regex=True)
        .str.split("M", expand=True)
    )
    time = time.astype(float)
    df["min"] = time[0] + (time[1] / 60)


def clean_combined_data(df):
    for col in Combined.STAT_CATEGORIES_INTEGER:
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(int)

    df.rename(columns=Combined.COLUMNS_TO_RENAME, inplace=True)

    time_to_float(df)

