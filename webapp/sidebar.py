import streamlit as st

from parameters import WebAppParameters


def set_defaults(challenge):
    if challenge:
        stat_categories = WebAppParameters.CHALLENGE_CATS
    else:
        stat_categories = WebAppParameters.DEFAULT_STAT_CATS

    return stat_categories


def create_sidebar(columns, season_avg_columns, len_df):
    # Button to refresh live data
    st.sidebar.button("Click Here to Refresh Live Data")

    challenge = st.sidebar.checkbox(
        "Check here to view current NBA Top Shot challenge", value=WebAppParameters.CHALLENGE_NOW
    )
    last_n_games = st.sidebar.selectbox(
        "Use season averages from the last __ games",
        WebAppParameters.LAST_N_GAMES_OPTIONS,
        WebAppParameters.LAST_N_GAMES_OPTIONS.index(WebAppParameters.DEFAULT_N_GAMES),
    )
    if last_n_games == "All":
        last_n_games = 0

    stat_categories = set_defaults(challenge)
    if challenge:
        st.sidebar.write(WebAppParameters.CHALLENGE_NAME)
        st.sidebar.write(WebAppParameters.CHALLENGE_DESC_EASY)
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
                value=WebAppParameters.NUM_HIGHLIGHTED,
                step=1,
            )
        else:
            how_many = 1
    else:
        options = stat_categories
        season_avg_options = None
        add_categories = None
        sub_categories = None
        how_many = 0

    return options, season_avg_options, add_categories, sub_categories, how_many, challenge
