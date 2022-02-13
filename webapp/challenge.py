import pandas as pd
import streamlit as st

from parameters import WeeklyChallengeParameters, DailyChallengeParameters
from webapp.utils import get_top_stats, get_top_stats_each_game, get_first_to_stats_each_team


def combine_top_prev_and_today(df_top_today, stat, df_top_prev=None, topshot_data_df=None):
    if df_top_prev is not None:
        df_top_prev = df_top_prev.join(topshot_data_df, how="left", on="name", lsuffix="",
                                       rsuffix="_TS").reset_index().set_index(
            ["name", "team"])
        df_top_prev.index = df_top_prev.index.set_levels(df_top_prev.index.levels[0] + " - 02/11", level=0)
        df_top = df_top_today.merge(df_top_prev, how="outer",
                                    on=["name", "team", stat, "differential",
                                        "plus_minus"] + DailyChallengeParameters.TOPSHOT_CATEGORIES)
        df_top = df_top.sort_values(stat, ascending=False)[:len(df_top_today)][
            [stat, "differential",
             "plus_minus"] + DailyChallengeParameters.TOPSHOT_CATEGORIES]
    else:
        df_top = df_top_today

    return df_top


def weekly_challenge(df=None, how_many=None, todays_games=None, start_times=None, today_dataset=None, options=None):
    if WeeklyChallengeParameters.CHALLENGE_DESC_HARD is not None:
        st.write(WeeklyChallengeParameters.CHALLENGE_DESC_HARD)

    st.sidebar.write(WeeklyChallengeParameters.CHALLENGE_NAME)
    st.sidebar.write(WeeklyChallengeParameters.CHALLENGE_DESC_EASY)

    list_top = None
    if WeeklyChallengeParameters.CHALLENGE_ADD_CATEGORIES is None:
        challenge_cats = WeeklyChallengeParameters.CHALLENGE_CATS
        sort_by = challenge_cats[0]
    else:
        challenge_cats = ["+".join(WeeklyChallengeParameters.CHALLENGE_ADD_CATEGORIES)]
        sort_by = challenge_cats[0]
    for cat in challenge_cats:
        if WeeklyChallengeParameters.TOP_STATS == "top_overall":
            add_to_list = get_top_stats(df, how_many, cat, WeeklyChallengeParameters.TIEBREAKERS)
        elif WeeklyChallengeParameters.TOP_STATS == "top_each":
            add_to_list = get_top_stats_each_game(df, todays_games, cat, WeeklyChallengeParameters.TIEBREAKERS)
        elif WeeklyChallengeParameters.TOP_STATS == "first_each":
            add_to_list = get_first_to_stats_each_team(df, todays_games, cat,
                                                       WeeklyChallengeParameters.FIRST_TO_THRESHOLD)
        list_top = pd.concat([list_top, add_to_list])

    if start_times[0] < today_dataset.now:
        sort_by = [sort_by] + WeeklyChallengeParameters.TIEBREAKERS
    else:
        sort_by = [sort_by] + WeeklyChallengeParameters.TIEBREAKERS + [sort_by + "_proj"]

    df_top = df[df.index.isin(list_top.index)][[options[0]] + ["on_court", "differential",
                                                               "plus_minus"] + WeeklyChallengeParameters.TOPSHOT_CATEGORIES].sort_values(
        sort_by[0], ascending=False)
    list_top = df_top

    st.write("### Friday Feb 4 & Saturday Feb 5 Challenge Moments")
    if WeeklyChallengeParameters.CHALLENGE_PREV is not None:
        st.write("### Previous Day Challenge Leaders")
        st.dataframe(WeeklyChallengeParameters.CHALLENGE_PREV)
    st.write("### Today's Challenge Leaders")
    if start_times[0] < today_dataset.now:
        st.dataframe(df_top)
    else:
        st.write("Today's games have not started yet.")

    st.title("Complete Leaderboard")
    st.write("**Projections are calculated as:**  \n" \
             "*live stat + ( stat average over games specified in sidebar \* mins remaining in game )*  \n" \
             "*OT periods add an additional 5 minutes to time remaining in game and projection is adjusted if OT is reached.  \n" \
             "Players with INJ or OUT injury status are projected 0 in all statistics."
             )
    return list_top, df_top, sort_by


def daily_challenge(df=None, how_many=None, todays_games=None, start_times=None, today_dataset=None, options=None,
                    topshot_data_df=None):
    if DailyChallengeParameters.CHALLENGE_DESC_HARD is not None:
        st.write(DailyChallengeParameters.CHALLENGE_DESC_HARD)

    st.sidebar.write(DailyChallengeParameters.CHALLENGE_NAME)
    st.sidebar.write(DailyChallengeParameters.CHALLENGE_DESC_EASY)

    list_top = None

    if DailyChallengeParameters.CHALLENGE_ADD_CATEGORIES is None:
        challenge_cats = DailyChallengeParameters.CHALLENGE_CATS
        sort_by = challenge_cats[0]
    else:
        challenge_cats = ["+".join(DailyChallengeParameters.CHALLENGE_ADD_CATEGORIES)]
        sort_by = challenge_cats[0]

    for cat in challenge_cats:
        if DailyChallengeParameters.TOP_STATS == "top_overall":
            add_to_list = get_top_stats(df, how_many, cat, DailyChallengeParameters.TIEBREAKERS)
        elif DailyChallengeParameters.TOP_STATS == "top_each":
            add_to_list = get_top_stats_each_game(df, todays_games, cat, DailyChallengeParameters.TIEBREAKERS)
        elif DailyChallengeParameters.TOP_STATS == "first_each":
            add_to_list = get_first_to_stats_each_team(df, todays_games, cat,
                                                       DailyChallengeParameters.FIRST_TO_THRESHOLD)
        list_top = pd.concat([list_top, add_to_list])

    if start_times[0] < today_dataset.now:
        sort_by = [sort_by] + DailyChallengeParameters.TIEBREAKERS
    else:
        sort_by = [sort_by] + DailyChallengeParameters.TIEBREAKERS + [sort_by + "_proj"]

    df_top = df[df.index.isin(list_top.index)][[options[0]] + ["on_court", "differential",
                                                               "plus_minus"] + DailyChallengeParameters.TOPSHOT_CATEGORIES].sort_values(
        sort_by[0], ascending=False)

    df_top = combine_top_prev_and_today(df_top, sort_by[0], df_top_prev=DailyChallengeParameters.CHALLENGE_PREV,
                                        topshot_data_df=topshot_data_df)
    list_top = df_top

    st.write("### Today's Challenge Leaders")
    st.write("For multiday Challenges - Any previous day's leaders are included.")
    if start_times[0] < today_dataset.now:
        st.dataframe(df_top)
    else:
        st.write("Today's games have not started yet.")

    st.title("Complete Leaderboard")
    st.write("**Projections are calculated as:**  \n" \
             "*live stat + ( stat average over games specified in sidebar \* mins remaining in game )*  \n" \
             "*OT periods add an additional 5 minutes to time remaining in game and projection is adjusted if OT is reached.  \n" \
             "Players with INJ or OUT injury status are projected 0 in all statistics."
             )
    return list_top, df_top, sort_by
