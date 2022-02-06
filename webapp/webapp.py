import ast
from cProfile import run

import pandas as pd

from webapp.utils import *


class WebApp:
    def __int__(self):
        pass

    def run_webapp(self):
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

        topshot_categories = (
            WebAppParameters.TS_EASY_CATS# + WebAppParameters.TS_HARD_CATS
        )

        # ----------------------------------------------------------------------
        last_n_games_options = ["All", 30, 14, 7]
        last_n_games = st.sidebar.selectbox(
            "Use season averages from the last n games",
            last_n_games_options,
            last_n_games_options.index(14),
        )
        if last_n_games == "All":
            last_n_games = 0

        # Create dataframe that webapp will be filtering
        today_dataset = CombinedStats(last_n_games=last_n_games)
        df = today_dataset.stats
        topshot_moments = today_dataset.topshot_data_df
        todays_games = today_dataset.todays_games_df
        start_times = todays_games["start_time"].to_list()
        tiebreakers = WebAppParameters.TIEBREAKERS

        columns = df.columns
        columns = columns.sort_values()

        season_avg_columns = [x + "_avg" for x in columns if x + "_avg" in columns]
        columns = [x for x in columns if x + "_avg" in columns]

        # Create a multiselect option for individual categories and generate prediction for each option selected
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

        options, options_proj = run_projections(
            df, options, add_categories, sub_categories
        )
        add_subtract_stat(df, add_categories, sub_categories)

        active_only = df["status"] == "ACTIVE"
        df_for_saving = df.copy().astype(str)
        multi_day_stat_list = []

        if WebAppParameters.IMPORT_ADDITIONAL_DAY:
            #multi_tiebreakers_list = []

            for stat in options:
                add_additional_stats(df, today_dataset.additional_stats_df, stat)
                multi_day_stat_list.append(stat+"_total")
            #for stat in WebAppParameters.TIEBREAKERS:
            #    add_additional_stats(df, today_dataset.additional_stats_df, stat)
            #    multi_tiebreakers_list.append(stat + "_total")
            options = multi_day_stat_list
            #tiebreakers = multi_tiebreakers_list

        # Multiple categories selected for adding and subtracting
        categories = (
            WebAppParameters.DEFAULT_CATS
            + options
            + season_avg_options
            + options_proj
            + [x for x in WebAppParameters.TIEBREAKERS if x != "min"]
            + topshot_categories
        )
        default_sort = options[0]
        if WebAppParameters.TOP_STATS_OVERALL:
            how_many = st.sidebar.slider(
                "Highlight the top ____ players in sorted categories",
                min_value=0,
                max_value=df.shape[0],
                value=WebAppParameters.NUM_HIGHLIGHTED,
                step=1,
            )

        sort_by = st.sidebar.selectbox(
            "Which category do you want to sort by?",
            options,
            options.index(default_sort),
        )

        # Button to refresh live data
        st.sidebar.button("Click Here to Refresh Live Data")
        bench_index = (df["starter"] != "Starter") & (df["status"] != "INACTIVE")

        if WebAppParameters.TOP_STATS_OVERALL:
            list_top = None
            for cat in WebAppParameters.CHALLENGE_CATS:
                add_to_list = get_top_stats(df, how_many, cat, WebAppParameters.TIEBREAKERS)
                if list_top is None:
                    list_top = add_to_list
                else:
                    list_top = pd.concat([list_top, add_to_list])

        if WebAppParameters.TOP_STATS_PER_GAME:
            list_top = pd.DataFrame()
            for cat in WebAppParameters.CHALLENGE_CATS:
                add_to_list = get_top_stats_each_game(df, today_dataset.todays_games_df, cat, WebAppParameters.TIEBREAKERS)
                if list_top is None:
                    list_top = add_to_list
                else:
                    list_top = pd.concat([list_top, add_to_list])

        if start_times[0] < today_dataset.now:
            sort_by = [sort_by] + WebAppParameters.TIEBREAKERS
        else:
            sort_by = [sort_by] + WebAppParameters.TIEBREAKERS + [sort_by + "_proj"]
        asc_list = [0] * len(sort_by)

        st.title("NBA Stat Tracker for {}".format(today_dataset.date))

        st.table(
            todays_games.reset_index()[
                ["game_status", "away_team", "away_score", "home_team", "home_score",]
            ]
        )
        st.title(WebAppParameters.CHALLENGE_NAME)
        st.write(WebAppParameters.CHALLENGE_DESC_EASY)
        if WebAppParameters.CHALLENGE_DESC_HARD is not None:
            st.write(WebAppParameters.CHALLENGE_DESC_HARD)
        for stat in multi_day_stat_list:
            st.write("*{} represent all stats accumulated since {}".format(
                stat, today_dataset.date_prev
            ))

        df = df.sort_values(sort_by, ascending=asc_list)[categories]

        dfStyler = df.style.set_properties(**{"text-align": "center"})
        dfStyler.set_table_styles(
            [dict(selector="th", props=[("text-align", "center")])]
        )
        df_all_challenge = topshot_moments[topshot_moments.index.isin(WebAppParameters.CHALLENGE_LEADERS)][topshot_categories]
        df_top = df[df.index.isin(list_top.index)][options + topshot_categories]

        st.title("Previous Day's Challenge Moments")
        st.dataframe(df_all_challenge)
        st.title("Today's Challenge Leaders")
        st.dataframe(df_top)
        st.title("Complete Leaderboard")
        if WebAppParameters.TOP_STATS_OVERALL:
            st.write("Green highlights are for the challenge stat leaders overall that have an eligible NBA Top Shot "
                     "moment.")
        if WebAppParameters.TOP_STATS_PER_GAME:
            st.write("Green highlights are for the challenge stat leaders in each game that have an eligible NBA Top "
                     "Shot moment.")
        # Options for Pandas DataFrame Style
        if count % 1 == 0 or count == 0:
            # if datetime.now > today_dataset.start_times[-1] + timedelta(hours=3):
            save_dataframe(df_for_saving)
            if start_times[0] < today_dataset.now:
                st.dataframe(
                    df.style.apply(bg_color, list_top=list_top), height=700
                )
            else:
                st.dataframe(df, height=700)
