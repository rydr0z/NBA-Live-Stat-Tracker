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
    df_modified = df.dropna(axis=0, subset=["set_easy"])[[stat]]
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
            return int(row["away_score"]) - int(row["home_score"])
        if row["awayorhome"] == "away":
            return int(row["home_score"]) - int(row["away_score"])


def df_create_columns(df):

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


def change_4h_percentage(df):
    col_list = ["4hchange_easy", "4hchange_hard"]
    for col in col_list:
        df[col] = df[col] / 100
        df[col] = df[col].map("{:.2%}".format)


def project_stat(row, stat):
    clock = row["game_clock"]
    avg_min = row["min_avg"]
    game_clock = row["game_status"]
    curr_stat = row[stat]
    avg_stat = row[stat + "_avg"]
    period = row["period"]
    if clock == "" or clock == np.nan or type(clock) == float:
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


def on_court_function(row):
    if row["period"] == 0 or row["game_status"] == "Final":
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
