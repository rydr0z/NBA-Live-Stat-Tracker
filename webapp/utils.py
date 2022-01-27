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


def run_webapp():
    st.sidebar.image(WebAppParameters.LOGO_PATH)

    count = st_autorefresh(
        interval=WebAppParameters.AUTO_REFRESH_INTERVAL,
        limit=WebAppParameters.AUTO_REFRESH_LIMIT,
        key="refreshapp",
    )

    # Custom CSS Styles and HTML
    with open(WebAppParameters.CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Set defaults:
    # ---------------------------------------------------------------------
    challenge = st.sidebar.checkbox(
        "Check here to use challenge settings", value=WebAppParameters.CHALLENGE_NOW
    )
    if challenge:
        stat_categories = WebAppParameters.CHALLENGE_CATS
    else:
        stat_categories = WebAppParameters.DEFAULT_STAT_CATS

    topshot_categories = WebAppParameters.TS_EASY_CATS + WebAppParameters.TS_HARD_CATS

    # ----------------------------------------------------------------------

    # Create dataframe that webapp will be filtering
    today_dataset = CombinedStats()
    df = today_dataset.stats
    todays_games = today_dataset.todays_games
    start_times = todays_games["start_time"].to_list()

    columns = df.columns
    columns = columns.sort_values()

    columns = [x for x in columns if x + "_avg" in columns]

    # Create a multiselect option for individual categories and generate prediction for each option selected
    options = st.sidebar.multiselect(
        "Which stats are you interested in?", columns, stat_categories
    )

    # create a multiselect option for adding multiple categories (cat1 + cat2 + cat3...)
    add_categories = st.sidebar.multiselect(
        "Do you want to add up any categories?", columns,
    )

    # create multiselect option for subtracting categories (cat1 - cat2 - cat3...)
    sub_categories = st.sidebar.multiselect(
        "Do you want to subtract any categories? Categories are subtracted from the first listed",
        columns,
    )

    options, options_proj = run_projections(df, options, add_categories, sub_categories)
    add_subtract_stat(df, add_categories, sub_categories)

    active_only = df["status"] == "ACTIVE"
    df_for_saving = df.copy().astype(str)

    if WebAppParameters.IMPORT_ADDITIONAL_DAY == True:
        import_additional_day(df)

    # Deal with different cases of Multiple categories being chosen
    # --------------------------------------------------------------

    # Multiple categories selected for adding and subtracting
    categories = (
        WebAppParameters.DEFAULT_CATS
        + options
        + options_proj
        + [x for x in WebAppParameters.TIEBREAKERS if x != "min"]
        + topshot_categories
    )
    default_sort = options[0]

    how_many = st.sidebar.slider(
        "Highlight the top ____ players in sorted category",
        min_value=0,
        max_value=df.shape[0],
        value=WebAppParameters.NUM_HIGHLIGHTED,
        step=1,
    )

    sort_by = st.sidebar.selectbox(
        "Which category do you want to sort by?", options, options.index(default_sort),
    )

    # Button to refresh live data
    st.sidebar.button("Click Here to Refresh Live Data")
    bench_index = (df["starter"] != "Starter") & (df["status"] != "INACTIVE")

    list_top = get_top_stats(df, how_many, sort_by, WebAppParameters.TIEBREAKERS)

    if start_times[0] < today_dataset.now:
        sort_by = [sort_by] + WebAppParameters.TIEBREAKERS
    else:
        sort_by = [sort_by] + WebAppParameters.TIEBREAKERS + [sort_by + "_proj"]
    asc_list = [0] * len(sort_by)

    st.title("NBA Stat Tracker for {}".format(today_dataset.date))
    # todays_games["Start Time"] = todays_games["Start Time"].dt.strftime(("%r EST"))
    # todays_games.set_index("Start Time", inplace=True)

    st.table(
        todays_games.reset_index()[
            ["game_status", "away_team", "away_score", "home_team", "home_score",]
        ]
    )

    df = df.sort_values(sort_by, ascending=asc_list)[categories]
    df.fillna("-", inplace=True)

    dfStyler = df.style.set_properties(**{"text-align": "center"})
    dfStyler.set_table_styles([dict(selector="th", props=[("text-align", "center")])])

    # Options for Pandas DataFrame Style
    if count % 1 == 0 or count == 0:
        # if datetime.now > today_dataset.start_times[-1] + timedelta(hours=3):
        df_for_saving.to_csv(
            path_or_buf="data/prevgamedays/"
            + datetime.now().strftime("%F")
            + "_NBAStats.csv"
        )
        if start_times[0] < today_dataset.now:
            if how_many == 0:
                st.dataframe(df, height=700)
            else:
                st.dataframe(df.style.apply(bg_color, list_top=list_top), height=700)
        else:
            st.dataframe(df, height=700)

