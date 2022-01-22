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


def game_clock_fn(row):
    if row["PERIOD"] == 0:
        return "Final"
    elif row["CLOCK"] == row["CLOCK"] and row["PERIOD"] == row["PERIOD"]:
        return "Q" + str(row["PERIOD"]) + " - " + str(row["CLOCK"])
    else:
        return "Game Not Started"


def bg_color(col, list_top):
    pd.options.display.precision = 2
    pd.options.display.float_format = "{:,.2f}".format

    color = "green"
    return [
        "background-color: %s" % color if i in list_top.index else ""
        for i, x in col.iteritems()
    ]


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
    df["SCORE"] = df["OWN_SCORE"].astype(str) + "-" + df["OPP_SCORE"].astype(str)
    df["GAME_CLOCK"] = df.apply(game_clock_fn, axis=1)


def project_stat(row, stat):
    clock = row["CLOCK"]
    avg_min = row["MIN_AVG"]
    game_clock = row["GAME_CLOCK"]
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
