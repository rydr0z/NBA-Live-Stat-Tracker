import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from data_combine.combinedata import CombinedStats
from parameters import WebAppParameters
from webapp.sidebar import create_sidebar
from webapp.utils import get_top_stats, get_top_stats_each_game, bg_color, add_subtract_stat, run_projections, \
    save_dataframe, get_first_to_stats_each_team


def run_webapp():
    st.sidebar.image("NBA Stat Logo.png")

    count = st_autorefresh(
        interval=WebAppParameters.AUTO_REFRESH_INTERVAL,
        limit=WebAppParameters.AUTO_REFRESH_LIMIT,
        key="refreshapp",
    )

    # Custom CSS Styles and HTML
    with open(WebAppParameters.CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    pd.options.display.float_format = '{:.2f}'.format
    pd.set_option("display.precision", 1)
    # Create dataframe that webapp will be filtering

    today_dataset = CombinedStats(last_n_games=WebAppParameters.DEFAULT_N_GAMES)
    df = today_dataset.stats
    todays_games = today_dataset.todays_games_df
    start_times = todays_games["start_time"].to_list()
    len_df = df.shape[0]

    columns = df.columns
    columns = columns.sort_values()

    season_avg_columns = [x + "_avg" for x in columns if x + "_avg" in columns]
    columns = [x for x in columns if x + "_avg" in columns]

    options, season_avg_options, add_categories, sub_categories, how_many, challenge = create_sidebar(columns,
                                                                                                      season_avg_columns,
                                                                                                      len_df)
    options, options_proj = run_projections(
        df, options, add_categories, sub_categories
    )
    add_subtract_stat(df, add_categories, sub_categories)

    df_for_saving = df.copy().astype(str)
    multi_day_stat_list = []

    ###################
    # Implement multiple days here.
    ###################

    # Multiple categories selected for adding and subtracting
    if todays_games["game_status"].str.contains("Final").all():
        options_proj = []
    if season_avg_options is not None:
        options = options + season_avg_options
    categories = (
            WebAppParameters.DEFAULT_CATS
            + options
            + options_proj
            + [x for x in WebAppParameters.TIEBREAKERS if x != "min"]
            + WebAppParameters.TOPSHOT_CATEGORIES
    )

    sort_by = options[0]
    st.title("Game Schedule for {}".format(today_dataset.date))

    st.table(
        todays_games.set_index(pd.Index(range(1, todays_games.shape[0] + 1)))[
            ["game_status", "away_team", "away_score", "home_team", "home_score"]
        ]
    )

    if WebAppParameters.CHALLENGE_DESC_HARD is not None:
        st.write(WebAppParameters.CHALLENGE_DESC_HARD)
    for stat in multi_day_stat_list:
        st.write("*{} represent all stats accumulated since {}".format(
            stat, today_dataset.date_prev
        ))

    df_styler = df.style.set_properties(**{"text-align": "center"})
    df_styler.set_table_styles(
        [dict(selector="th", props=[("text-align", "center")])]
    )

    if challenge:
        list_top = None

        for cat in WebAppParameters.CHALLENGE_CATS:
            if WebAppParameters.TOP_STATS == "top_overall":
                add_to_list = get_top_stats(df, how_many, cat, WebAppParameters.TIEBREAKERS)
            elif WebAppParameters.TOP_STATS == "top_each":
                add_to_list = get_top_stats_each_game(df, todays_games, cat, WebAppParameters.TIEBREAKERS)
            elif WebAppParameters.TOP_STATS == "first_each":
                add_to_list = get_first_to_stats_each_team(df, todays_games, cat, WebAppParameters.FIRST_TO_THRESHOLD)
            list_top = pd.concat([list_top, add_to_list])

        if start_times[0] < today_dataset.now:
            sort_by = [sort_by] + WebAppParameters.TIEBREAKERS
        else:
            sort_by = [sort_by] + WebAppParameters.TIEBREAKERS + [sort_by + "_proj"]
        # df_all_challenge = topshot_moments[topshot_moments.index.isin(WebAppParameters.CHALLENGE_LEADERS)][
        #    WebAppParameters.TOPSHOT_CATEGORIES]
        df_top = df[df.index.isin(list_top.index)][options + WebAppParameters.TOPSHOT_CATEGORIES]

        # st.write("### Friday Feb 4 & Saturday Feb 5 Challenge Moments")
        # st.dataframe(df_all_challenge)
        st.write("### Today's Challenge Leaders")
        if start_times[0] < today_dataset.now:
            st.dataframe(df_top)
        else:
            st.write("Today's games have not started yet.")

    st.title("Complete Leaderboard")
    st.write("**Projections are calculated as:**")
    st.write(
        "*live stat + ( stat average over games specified in sidebar \* mins remaining in game )*")
    st.write(
        "*OT periods add an additional 5 minutes to time remaining in game and projection is adjusted if OT is reached."
        " Players with INJ status are projected 0 in all statistics."
    )

    df = df.sort_values(sort_by, ascending=False)[categories]
    # Options for Pandas DataFrame Style
    if count % 1 == 0 or count == 0:
        # if datetime.now > today_dataset.start_times[-1] + timedelta(hours=3):
        save_dataframe(df_for_saving)
        if start_times[0] < today_dataset.now and challenge:
            st.dataframe(
                df.style.apply(bg_color, list_top=list_top).set_precision(2), height=700
            )
        else:
            st.dataframe(df.style.set_precision(2), height=700)
