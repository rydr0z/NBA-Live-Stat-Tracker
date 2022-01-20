import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
import numpy as np
import time

from nba_boxscore_fetcher import Stat_Dataset

with open("frontend/css/streamlit.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

tiebreakers = ["FGM", "DIFFERENTIAL", "PLUS_MINUS", "MIN"]


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


pd.options.display.precision = 2

today_dataset = Stat_Dataset()
df = today_dataset.gameday_df


def bg_color(col):
    color = "green"
    return [
        "background-color: %s" % color if i in list_largest.index else ""
        for i, x in col.iteritems()
    ]


def bg_color2(col):
    color = "yellow"
    return [
        "background-color: %s" % color if i in list_playing.index else ""
        for i, x in col.iteritems()
    ]


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

df.rename(columns={"TEAM_NBA": "TEAM"}, inplace=True)


def game_clock_fn(row):
    if row["PERIOD"] != 0 and row["PERIOD"] != np.nan:
        return "Q" + str(row["PERIOD"]) + " - " + str(row["CLOCK"])
    if row["PERIOD"] == 0:
        return "Final"
    else:
        return np.nan


df["GAME_CLOCK"] = df.apply(game_clock_fn, axis=1)

list_playing = df[df["GAME_CLOCK"] != "Final"]

list_largest = get_top_stats(df, 7, "FGA", tiebreakers)

fixed_categories = ["OPP", "SCORE", "GAME_CLOCK", "MIN"]
EASY_categories = ["EASY_MOMENT", "COUNT_EASY", "LOW_ASK_EASY"]
HARD_categories = ["HARD_MOMENT", "COUNT_HARD", "LOW_ASK_HARD"]
topshot_categories = EASY_categories + HARD_categories


columns = df.columns
columns = [x.upper() for x in columns]
columns.sort()

challenge_cats = ["FGA"]

stat_categories = ["PTS", "REB", "AST", "STL", "BLK"]
options = st.sidebar.multiselect(
    "Which stats are you interested in?", columns, challenge_cats
)


def project_stat(row):
    clock = row["CLOCK"]
    avg_min = row["MIN_AVG"]
    curr_min = row["MIN"]
    game_clock = row["GAME_CLOCK"]
    curr_stat = row[stat]
    avg_stat = row[stat + "_AVG"]
    period = row["PERIOD"]
    if clock == np.nan or clock == "" or game_clock == "Final" or type(clock) == float:
        return row[stat]
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


for option in options:
    stat = option
    df[stat + "_PROJ"] = 0
    df[stat + "_PROJ"] = df.apply(project_stat, axis=1)

stat = ["FGA"]

options_proj = [x + "_PROJ" for x in options]
# options_proj = list(set(options_proj) - (set(options_proj) - set(df.columns)))

add_categories = st.sidebar.multiselect(
    "Do you want to add up any categories?", columns
)
add_categories_combined = "+".join(add_categories)

sub_categories = st.sidebar.multiselect(
    "Do you want to subtract any categories? Categories are subtracted from the first listed",
    columns,
)
sub_categories_combined = "-".join(sub_categories)

challenge = st.sidebar.checkbox("Check here to use challenge settings")

st.sidebar.button("Click Here to Refresh Live Data")
if add_categories:
    df[add_categories_combined] = 0

    for cat in add_categories:
        df[add_categories_combined] += df[cat]

if sub_categories:
    df[sub_categories_combined] = df[sub_categories[0]]

    for cat in sub_categories:
        if cat != sub_categories[0]:
            df[sub_categories_combined] -= df[cat]

if add_categories and sub_categories:
    categories = (
        fixed_categories
        + [add_categories_combined, sub_categories_combined]
        + options
        + topshot_categories
    )
    sort_by = [add_categories_combined, sub_categories_combined] + tiebreakers
    asc_list = [0] * len(sort_by)
elif add_categories:
    categories = (
        fixed_categories + [add_categories_combined] + options + topshot_categories
    )
    sort_by = [add_categories_combined] + tiebreakers
    asc_list = [0] * len(sort_by)
elif sub_categories:
    categories = (
        fixed_categories + [sub_categories_combined] + options + topshot_categories
    )
    sort_by = [sub_categories_combined] + tiebreakers
    asc_list = [0] * len(sort_by)
else:
    categories = fixed_categories + options + options_proj + topshot_categories
    sort_by = stat + tiebreakers
    asc_list = [0] * len(sort_by)

active_only = df["STATUS"] == "ACTIVE"

if challenge:
    categories = fixed_categories + challenge_cats + options_proj + topshot_categories
    options = challenge_cats
    sort_by = challenge_cats + tiebreakers
    asc_list = [0] * len(sort_by)

todays_games = pd.DataFrame(
    today_dataset.todays_games, index=today_dataset.start_times, columns=["Game"]
)
st.write("NBA Stat Tracker for {}".format(today_dataset.game_date))
st.table(todays_games.sort_values(by=["Game"]).sort_index())

df = df.sort_values(sort_by, ascending=asc_list)[categories]

st.dataframe(df.style.apply(bg_color), height=1200)
