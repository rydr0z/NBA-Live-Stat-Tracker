import pandas as pd
from datetime import datetime
import streamlit as st
import numpy as np
from streamlit_autorefresh import st_autorefresh
from webapp.utils import *
from data_combine.combinedata import CombinedStats
from webapp.constants import WebAppParameters


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


def import_additional_day(df):
    df_previous = pd.read_csv(
        WebAppParameters.ADDITIONAL_DAY_PATH, dtype=df.dtypes.to_dict()
    )
    df_previous.fillna(0, inplace=True)
    df_previous.set_index(["name", "team"], inplace=True)
    df = pd.concat([df, df_previous])


def add_subtract_stat(df, add_categories, sub_categories):
    add_categories_str = "+".join(add_categories)
    sub_categories_str = "-".join(sub_categories)

    if add_categories:
        df[add_categories_str] = 0

        for cat in add_categories:
            df[add_categories_str] += df[cat]

    if sub_categories:
        df[sub_categories_str] = df[sub_categories[0]]

        for cat in sub_categories:
            if cat != sub_categories[0]:
                df[sub_categories_str] -= df[cat]


def run_projections(df, options, add_categories, sub_categories):

    add_categories_str = "+".join(add_categories)
    sub_categories_str = "-".join(sub_categories)

    for option in options:
        df[option + "_proj"] = df.apply(project_stat, stat=option, axis=1)

    if add_categories or sub_categories:
        df[add_categories_str + "_proj"] = 0
        df[sub_categories_str + "_proj"] = 0
        for cat in add_categories:
            df[add_categories_str + "_proj"] += df.apply(project_stat, stat=cat, axis=1)
        for cat in sub_categories:
            if cat == sub_categories[0]:
                df[sub_categories_str + "_proj"] = df.apply(
                    project_stat, stat=cat, axis=1
                )
            else:
                df[sub_categories_str + "_proj"] -= df.apply(
                    project_stat, stat=cat, axis=1
                )
    options = [add_categories_str, sub_categories_str] + options
    options = list(filter(None, options))

    options_proj = [x + "_proj" for x in options]

    return options, options_proj

def save_dataframe(df):
    df.to_csv(
        path_or_buf=WebAppParameters.PATH_SAVE
        + datetime.now().strftime("%F")
        + WebAppParameters.FILE_NAME_SAVE
    )

