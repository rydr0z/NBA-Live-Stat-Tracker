from cProfile import run
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
            WebAppParameters.TS_EASY_CATS + WebAppParameters.TS_HARD_CATS
        )

        # ----------------------------------------------------------------------

        # Create dataframe that webapp will be filtering
        today_dataset = CombinedStats()
        df = today_dataset.stats
        todays_games = today_dataset.todays_games_df
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

        options, options_proj = run_projections(
            df, options, add_categories, sub_categories
        )
        add_subtract_stat(df, add_categories, sub_categories)

        active_only = df["status"] == "ACTIVE"
        df_for_saving = df.copy().astype(str)

        if WebAppParameters.IMPORT_ADDITIONAL_DAY == True:
            import_additional_day(df)

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
            "Which category do you want to sort by?",
            options,
            options.index(default_sort),
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

        st.table(
            todays_games.reset_index()[
                ["game_status", "away_team", "away_score", "home_team", "home_score",]
            ]
        )

        df = df.sort_values(sort_by, ascending=asc_list)[categories]
        df.fillna("-", inplace=True)

        dfStyler = df.style.set_properties(**{"text-align": "center"})
        dfStyler.set_table_styles(
            [dict(selector="th", props=[("text-align", "center")])]
        )

        # Options for Pandas DataFrame Style
        if count % 1 == 0 or count == 0:
            # if datetime.now > today_dataset.start_times[-1] + timedelta(hours=3):
            save_dataframe(df_for_saving)
            if start_times[0] < today_dataset.now:
                if how_many == 0:
                    st.dataframe(df, height=700)
                else:
                    st.dataframe(
                        df.style.apply(bg_color, list_top=list_top), height=700
                    )
            else:
                st.dataframe(df, height=700)
