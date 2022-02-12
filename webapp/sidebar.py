import streamlit as st

from parameters import WebAppParameters, WeeklyChallengeParameters, DailyChallengeParameters


def set_defaults(challenge, challenge_type):
    if challenge:
        if challenge_type == "Weekly":
            stat_categories = WeeklyChallengeParameters.CHALLENGE_CATS
            tiebreakers = WeeklyChallengeParameters.TIEBREAKERS
        elif challenge_type == "Daily":
            stat_categories = DailyChallengeParameters.CHALLENGE_CATS
            tiebreakers = DailyChallengeParameters.TIEBREAKERS
    else:
        stat_categories = WebAppParameters.DEFAULT_STAT_CATS
        tiebreakers = WebAppParameters.TIEBREAKERS

    return stat_categories, tiebreakers


def create_sidebar(columns, season_avg_columns, len_df):
    # Button to refresh live data
    st.sidebar.button("Click Here to Refresh Live Data")

    challenge = st.sidebar.checkbox(
        "Check here to view current NBA Top Shot challenge", value=WebAppParameters.CHALLENGE_NOW
    )
    challenge_type = None
    if challenge:
        challenge_type = st.sidebar.selectbox(
            "Which challenge do you want to view:",
            ["Weekly", "Daily"],
            ["Weekly", "Daily"].index(WebAppParameters.CHALLENGE_TYPE)
        )
    last_n_games = st.sidebar.selectbox(
        "Use season averages from the last __ games",
        WebAppParameters.LAST_N_GAMES_OPTIONS,
        WebAppParameters.LAST_N_GAMES_OPTIONS.index(WebAppParameters.DEFAULT_N_GAMES),
    )
    if last_n_games == "All":
        last_n_games = 0

    stat_categories, tiebreakers = set_defaults(challenge, challenge_type)

    if not challenge:
        options = st.sidebar.multiselect(
            "Which live game stats are you interested in?", columns, stat_categories
        )
        season_avg_options = st.sidebar.multiselect(
            "Which season average stats are you interested in?", season_avg_columns
        )
        # create a multiselect option for adding multiple categories (cat1 + cat2 + cat3...)
        add_categories = st.sidebar.multiselect(
            "Do you want to add up any categories?", columns
        )

        # create multiselect option for subtracting categories (cat1 - cat2 - cat3...)
        sub_categories = st.sidebar.multiselect(
            "Do you want to subtract any categories? Categories are subtracted from the first listed",
            columns,
        )
        if WebAppParameters.TOP_STATS == "top_overall":
            how_many = st.sidebar.slider(
                "Highlight the top __ players in sorted categories",
                min_value=0,
                max_value=len_df,
                value=0,
                step=1,
            )
        else:
            how_many = 1
    else:
        if challenge_type == "Weekly":
            options = stat_categories
            season_avg_options = WeeklyChallengeParameters.CHALLENGE_SEASON_AVG_OPTIONS
            add_categories = WeeklyChallengeParameters.CHALLENGE_ADD_CATEGORIES
            sub_categories = WeeklyChallengeParameters.CHALLENGE_SUB_CATEGORIES
            how_many = WeeklyChallengeParameters.CHALLENGE_NUM_HIGHLIGHTED
        if challenge_type == "Daily":
            options = stat_categories
            season_avg_options = DailyChallengeParameters.CHALLENGE_SEASON_AVG_OPTIONS
            add_categories = DailyChallengeParameters.CHALLENGE_ADD_CATEGORIES
            sub_categories = DailyChallengeParameters.CHALLENGE_SUB_CATEGORIES
            how_many = DailyChallengeParameters.CHALLENGE_NUM_HIGHLIGHTED

    return options, season_avg_options, add_categories, sub_categories, how_many, tiebreakers, challenge, challenge_type
