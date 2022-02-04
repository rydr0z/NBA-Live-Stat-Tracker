import pandas as pd
import streamlit as st
import numpy as np
from data_combine.constants import CombinedParameters


def combine_data(todays_games_df, daily_stats_df, season_stats_df, topshot_data_df, injury_report_df,
                 additional_stats_df):
    """This is the function for combining the data fetched from various sources"""
    season_stats_df.set_index(["name", "team"], inplace=True)
    if additional_stats_df is not None:
        additional_stats_df.set_index(["name", "team"], inplace=True)
        season_stats_df = season_stats_df.join(
            additional_stats_df, on=["name", "team"], lsuffix="", rsuffix="_prev", how="outer"
        )

    daily_stats_df.set_index(["name", "team"], inplace=True)
    stats_df = season_stats_df.join(
        daily_stats_df, on=["name", "team"], lsuffix="_avg", rsuffix="",
    )
    stats_df.reset_index(inplace=True)
    stats_df["game_id"] = stats_df["game_id_avg"]

    stats_df.set_index("name", inplace=True)
    stats_df = stats_df.join(topshot_data_df, on="name", lsuffix="_nba", rsuffix="_TS")

    injury_report_df.set_index("name", inplace=True)
    stats_df = stats_df.join(injury_report_df, on="name")

    stats_df.reset_index(inplace=True)
    stats_df.set_index("game_id", inplace=True)
    todays_games_df.set_index("game_id", inplace=True)
    stats_df = stats_df.join(todays_games_df, on="game_id")

    stats_df.reset_index(inplace=True)
    stats_df.rename(columns={"team_nba": "team"}, inplace=True)
    stats_df.set_index(["name", "team"], inplace=True)

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


def score_function(row):
    if row["period"] == 0:
        return "-"
    else:
        if row["awayorhome"] == "home":
            return str(row["away_score"]) + "-" + str(row["home_score"])
        if row["awayorhome"] == "away":
            return str(row["home_score"]) + "-" + str(row["away_score"])


def differential_function(row):
    if row["period"] == 0:
        return "-"
    else:
        if row["awayorhome"] == "home":
            return int(row["home_score"]) - int(row["away_score"])
        if row["awayorhome"] == "away":
            return int(row["away_score"]) - int(row["home_score"])


def on_court_function(row):
    if row["injury_status"] is not np.nan:
        return row["injury_status"]
    elif row["period"] == 0 or row["game_status"] == "Final" or row["game_status"] == "Final/OT":
        return "-"
    else:
        if row["on_court"] == "1":
            return "In Game"
        if row["on_court"] == "0":
            return "On Bench"


def starter_function(row):
    if row["period"] == 0:
        return "-"
    else:
        if row["starter"] == "1":
            return "Starter"
        if row["starter"] == "0":
            return "Bench"


def clean_and_create_columns(df):
    for col in CombinedParameters.STAT_CATEGORIES_INTEGER:
        df[col] = df[col].fillna(0)
        df[col] = df[col].astype(int)

    df.rename(columns=CombinedParameters.COLUMNS_TO_RENAME, inplace=True)

    time_to_float(df)

    df["easy_moment"] = (
            df["set_easy"]
            + "-"
            + df["tier_easy"]
            + "-"
            + df["series_easy"]
            + "-"
            + df["play_easy"]
    )
    df["hard_moment"] = (
            df["set_hard"]
            + "-"
            + df["tier_hard"]
            + "-"
            + df["series_hard"]
            + "-"
            + df["play_hard"]
    )

    away_index = df["awayorhome"] == "home"
    home_index = df["awayorhome"] == "away"
    df["away_score"].fillna(0, inplace=True)
    df["home_score"].fillna(0, inplace=True)

    df["score"] = df.apply(score_function, axis=1)
    df["differential"] = df.apply(differential_function, axis=1)
    df["on_court"] = df.apply(on_court_function, axis=1)
    df["starter"] = df.apply(starter_function, axis=1)
