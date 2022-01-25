import numpy as np
import streamlit as st
import pandas as pd
from datetime import datetime


def get_top_stats(df, num, stat, tiebreakers):
    # sort by tiebreakers first
    # (team point differential -> plus minus -> minutes)
    df.sort_values(
        tiebreakers, inplace=True, ascending=False,
    )
    df_modified = df.dropna(axis=0, subset=["SET_EASY"])[[stat]]
    if df_modified[stat].dtype == object:
        list_largest = df_modified.sort_values(by=stat, ascending=False)[:num]
    else:
        list_largest = df_modified.nlargest(num, stat)
    return list_largest


def bg_color(col, list_top):
    pd.options.display.precision = 2
    pd.options.display.float_format = "{:,.2f}".format

    color = "green"
    return [
        "background-color: %s" % color if i in list_top.index else ""
        for i, x in col.iteritems()
    ]


def score_function(row):
    if row["PERIOD"] == 0:
        return "-"
    else:
        if row["AWAYORHOME"] == "home":
            return str(row["AWAY_SCORE"]) + "-" + str(row["HOME_SCORE"])
        if row["AWAYORHOME"] == "away":
            return str(row["HOME_SCORE"]) + "-" + str(row["AWAY_SCORE"])


def differential_function(row):
    if row["PERIOD"] == 0:
        return "-"
    else:
        if row["AWAYORHOME"] == "home":
            return int(row["AWAY_SCORE"]) - int(row["HOME_SCORE"])
        if row["AWAYORHOME"] == "away":
            return int(row["HOME_SCORE"]) - int(row["AWAY_SCORE"])


def df_create_columns(df):

    df["EASY_MOMENT"] = (
        df["SET_EASY"]
        + "-"
        + df["TIER_EASY"]
        + "-"
        + df["SERIES_EASY"]
        + "-"
        + df["PLAY_EASY"]
    )
    df["HARD_MOMENT"] = (
        df["SET_HARD"]
        + "-"
        + df["TIER_HARD"]
        + "-"
        + df["SERIES_HARD"]
        + "-"
        + df["PLAY_HARD"]
    )

    away_index = df["AWAYORHOME"] == "home"
    home_index = df["AWAYORHOME"] == "away"
    df["AWAY_SCORE"].fillna(0, inplace=True)
    df["HOME_SCORE"].fillna(0, inplace=True)

    df["SCORE"] = df.apply(score_function, axis=1)
    df["DIFFERENTIAL"] = df.apply(differential_function, axis=1)


def change_4h_percentage(df):
    col_list = ["4HCHANGE_EASY", "4HCHANGE_HARD"]
    for col in col_list:
        df[col] = df[col] / 100
        df[col] = df[col].map("{:.2%}".format)


def project_stat(row, stat):
    clock = row["GAME_CLOCK"]
    avg_min = row["MIN_AVG"]
    game_clock = row["GAME_CLOCK_"]
    curr_stat = row[stat]
    avg_stat = row[stat + "_AVG"]
    period = row["PERIOD"]
    if clock == np.nan or type(clock) == float:
        return avg_stat
    elif game_clock == "Final" or period == 0 or clock == "":
        return curr_stat
    elif avg_min == 0 or avg_min == np.nan:
        return 0
    elif float(period) < 5:
        time = clock.split(":")
        time = float(time[0]) + (float(time[1]) / 60)
        return float(curr_stat) + (float(avg_stat) / 48.0) * (
            48 - (float(period) * 12) + float(time)
        )
    else:
        time = clock.split(":")
        time = float(time[0]) + (float(time[1]) / 60)
        return float(curr_stat) + (float(avg_stat) / 48.0) * float(time)


def time_to_float(df):
    df["MIN"] = df["MIN"].fillna("PT00M00.00S")
    time = (
        df["MIN"]
        .str.replace("PT", "", regex=True)
        .str.replace("S", "", regex=True)
        .str.split("M", expand=True)
    )
    time = time.astype(float)
    df["MIN"] = time[0] + (time[1] / 60)


def on_court_function(row):
    if row["PERIOD"] == 0 or row["GAME_STATUS"] == "Final":
        return "-"
    else:
        if row["ONCOURT"] == "1":
            return "In Game"
        if row["ONCOURT"] == "0":
            return "On Bench"


def starter_function(row):
    if row["PERIOD"] == 0:
        return "-"
    else:
        if row["STARTER"] == "1":
            return "Starter"
        if row["STARTER"] == "0":
            return "Bench"
