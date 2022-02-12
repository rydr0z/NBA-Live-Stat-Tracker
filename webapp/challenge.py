import pandas as pd
import streamlit as st

from parameters import WeeklyChallengeParameters, DailyChallengeParameters
from webapp.utils import get_top_stats, get_top_stats_each_game, get_first_to_stats_each_team


def weekly_challenge(df=None, how_many=None, todays_games=None, start_times=None, today_dataset=None,
                     sort_by=None, options=None):
    if WeeklyChallengeParameters.CHALLENGE_DESC_HARD is not None:
        st.write(WeeklyChallengeParameters.CHALLENGE_DESC_HARD)

    st.sidebar.write(WeeklyChallengeParameters.CHALLENGE_NAME)
    st.sidebar.write(WeeklyChallengeParameters.CHALLENGE_DESC_EASY)

    list_top = None

    for cat in WeeklyChallengeParameters.CHALLENGE_CATS:
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
    # df_all_challenge = topshot_moments[topshot_moments.index.isin(WeeklyChallengeParameters.CHALLENGE_LEADERS)][
    #    WeeklyChallengeParameters.TOPSHOT_CATEGORIES]
    df_top = df[df.index.isin(list_top.index)][options + WeeklyChallengeParameters.TOPSHOT_CATEGORIES]

    # st.write("### Friday Feb 4 & Saturday Feb 5 Challenge Moments")
    # st.dataframe(df_all_challenge)
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


def daily_challenge(df=None, how_many=None, todays_games=None, start_times=None, today_dataset=None,
                    sort_by=None, options=None):
    if DailyChallengeParameters.CHALLENGE_DESC_HARD is not None:
        st.write(DailyChallengeParameters.CHALLENGE_DESC_HARD)

    st.sidebar.write(DailyChallengeParameters.CHALLENGE_NAME)
    st.sidebar.write(DailyChallengeParameters.CHALLENGE_DESC_EASY)

    list_top = None

    for cat in DailyChallengeParameters.CHALLENGE_CATS:
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
    # df_all_challenge = topshot_moments[topshot_moments.index.isin(DailyChallengeParameters.CHALLENGE_LEADERS)][
    #    DailyChallengeParameters.TOPSHOT_CATEGORIES]
    df_top = df[df.index.isin(list_top.index)][options + DailyChallengeParameters.TOPSHOT_CATEGORIES]

    # st.write("### Friday Feb 4 & Saturday Feb 5 Challenge Moments")
    # st.dataframe(df_all_challenge)
    if DailyChallengeParameters.CHALLENGE_PREV is not None:
        st.write("### Previous Day Challenge Leaders")
        st.dataframe(DailyChallengeParameters.CHALLENGE_PREV)
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
