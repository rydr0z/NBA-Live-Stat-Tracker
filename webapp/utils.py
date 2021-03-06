import os
from datetime import datetime

import numpy as np
import pandas as pd

from parameters import WebAppParameters


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


def get_top_stats_each_game(df, todays_games, stat, tiebreakers):
    # sort by tiebreakers first
    # (team point differential -> plus minus -> minutes)
    df.sort_values(
        tiebreakers, inplace=True, ascending=False,
    )
    list_largest = pd.DataFrame()
    for index, game in todays_games.iterrows():
        df_game = df[df["game_id"] == index]
        df_game = df_game.dropna(axis=0, subset=["set_easy"])[[stat]]
        if df_game[stat].dtype == object:
            largest = df_game.sort_values(by=stat, ascending=False)[:1]
        else:
            largest = df_game.nlargest(1, stat)
        list_largest = pd.concat([list_largest, largest])
    return list_largest


def get_first_to_stats_each_team(df, todays_games, stat, threshold):
    # sort by tiebreakers first
    # (team point differential -> plus minus -> minutes)
    if os.path.isfile('list_first.pkl'):
        list_first = pd.read_pickle("list_first.pkl")
    else:
        list_first = pd.DataFrame(columns=["name", "team"])
        list_first['name'] = WebAppParameters.CHALLENGE_LEADERS
        list_first['team'] = WebAppParameters.CHALLENGE_LEADERS_TEAMS
        list_first.set_index(["name", "team"], inplace=True)
    teams = pd.concat([todays_games['away_team'], todays_games['home_team']]).unique()
    list_largest = pd.DataFrame()
    for team in teams:
        df_game = df.xs(team, level=1, drop_level=False)
        df_game = df_game.dropna(axis=0, subset=["set_easy"])[[stat]]
        largest = df_game.sort_values(by=stat, ascending=False)[:1]
        first = df_game[df_game[stat] == threshold]
        if ~first.index.get_level_values(level=1).isin(list_first.index.get_level_values(level=1)).any():
            list_first = pd.concat([list_first, first])
        list_largest = pd.concat([list_largest, largest])
    list_largest = list_largest[
        ~list_largest.index.get_level_values(level=1).isin(list_first.index.get_level_values(level=1))]
    list_return = pd.concat([list_first, list_largest])
    list_first.to_pickle("list_first.pkl")
    return list_return


def bg_color(col, list_top):
    pd.options.display.precision = 2
    pd.options.display.float_format = "{:,.2f}".format

    color = "green"
    return [
        "background-color: %s" % color if i in list_top.index else ""
        for i, x in col.iteritems()
    ]


def project_stat(row, stat):
    inj = row["injury_status"]
    clock = row["game_clock"]
    avg_min = row["min_avg"]
    game_clock = row["game_status"]
    curr_stat = row[stat]
    avg_stat = row[stat + "_avg"]
    period = row["period"]
    if game_clock == "Final" or game_clock == "Final/OT":
        return float(curr_stat)
    elif avg_min == 0 or avg_min == np.nan or "INJ" in str(inj) or "OUT" in str(inj):
        return 0.0
    elif clock == np.nan or type(clock) == float or period == 0 or clock == "":
        return float(avg_stat)
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
    if add_categories is not None:
        if len(add_categories) > 1:
            add_categories_str = "+".join(add_categories)
            df[add_categories_str] = 0

            for cat in add_categories:
                df[add_categories_str] += df[cat]
    if sub_categories is not None:
        if len(sub_categories) > 1:
            sub_categories_str = "-".join(sub_categories)

            df[sub_categories_str] = df[sub_categories[0]]

            for cat in sub_categories:
                if cat != sub_categories[0]:
                    df[sub_categories_str] -= df[cat]


def run_projections(df, options, add_categories, sub_categories):
    options_operations = []
    if add_categories is not None:
        if len(add_categories) > 1:
            add_categories_str = "+".join(add_categories)
            df[add_categories_str + "_proj"] = 0
            for cat in add_categories:
                df[add_categories_str + "_proj"] += df.apply(project_stat, stat=cat, axis=1)
            options_operations.append(add_categories_str)
    if sub_categories is not None:
        if len(sub_categories) > 1:
            sub_categories_str = "-".join(sub_categories)
            df[sub_categories_str + "_proj"] = 0
            for cat in sub_categories:
                if cat == sub_categories[0]:
                    df[sub_categories_str + "_proj"] = df.apply(
                        project_stat, stat=cat, axis=1
                    )
                else:
                    df[sub_categories_str + "_proj"] -= df.apply(
                        project_stat, stat=cat, axis=1
                    )
            options_operations.append(sub_categories_str)

    for option in options:
        df[option + "_proj"] = df.apply(project_stat, stat=option, axis=1)

    options = options_operations + options
    options = list(filter(None, options))

    options_proj = [x + "_proj" for x in options]

    return options, options_proj


def save_dataframe(df):
    df.to_csv(
        path_or_buf=WebAppParameters.PATH_SAVE
                    + datetime.now().strftime("%F")
                    + WebAppParameters.FILE_NAME_SAVE
    )


def add_additional_stats(df, additional_stats, stat):
    additional_stats.reset_index(inplace=True)
    additional_stats.groupby(['name']).sum()
    additional_stats.set_index(['name', 'team'], inplace=True)
    if additional_stats is not None:
        df[stat + "_total"] = df[stat]
        df[stat + "_total"] += additional_stats[stat]
        df.loc[df[stat + "_total"].isna(), stat + "_total"] = df[stat]
