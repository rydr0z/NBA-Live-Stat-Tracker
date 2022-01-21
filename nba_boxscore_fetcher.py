import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
import numpy as np
import time

from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import boxscore
from nba_api.stats.endpoints import teamplayerdashboard


@st.cache(allow_output_mutation=True)
def get_team_stats(team_id):
    team_player_dash = teamplayerdashboard.TeamPlayerDashboard(team_id, timeout=120)
    time.sleep(2)
    dict = team_player_dash.get_dict()
    data = dict["resultSets"][1]["rowSet"]
    columns = dict["resultSets"][1]["headers"]

    df_team = pd.DataFrame(data=data, columns=columns)
    columns_to_avg = [
        "MIN",
        "FGM",
        "FGA",
        "FG3M",
        "FG3A",
        "FTM",
        "FTA",
        "OREB",
        "DREB",
        "REB",
        "AST",
        "TOV",
        "STL",
        "BLK",
        "BLKA",
        "PF",
        "PFD",
        "PTS",
    ]
    columns_to_drop = [
        "GROUP_SET",
        "NICKNAME",
        "NBA_FANTASY_PTS",
        "GP_RANK",
        "W_RANK",
        "L_RANK",
        "W_PCT_RANK",
        "MIN_RANK",
        "FGM_RANK",
        "FGA_RANK",
        "FG_PCT_RANK",
        "FG3M_RANK",
        "FG3A_RANK",
        "FG3_PCT_RANK",
        "FTM_RANK",
        "FTA_RANK",
        "FT_PCT_RANK",
        "OREB_RANK",
        "DREB_RANK",
        "REB_RANK",
        "AST_RANK",
        "TOV_RANK",
        "STL_RANK",
        "BLK_RANK",
        "BLKA_RANK",
        "PF_RANK",
        "PFD_RANK",
        "PTS_RANK",
        "PLUS_MINUS_RANK",
        "NBA_FANTASY_PTS_RANK",
        "DD2_RANK",
        "TD3_RANK",
    ]
    df_team[columns_to_avg] = df_team[columns_to_avg].div(df_team["GP"].values, axis=0)
    df_team.drop(columns=columns_to_drop, inplace=True)
    df_team.rename(columns={"PLAYER_NAME": "NAME"}, inplace=True)
    return df_team


class Stat_Dataset:

    # all stat categories that can be converted to int later on
    stat_categories_integer = [
        "AST",
        "BLK",
        "BLKR",
        "FGA",
        "FGM",
        "PF_OFF",
        "PFD",
        "PF",
        "PF_TECH",
        "FTA",
        "FTM",
        "MINUS",
        "PLUS",
        "PLUS_MINUS",
        "PTS",
        "PTS_FASTBREAK",
        "PTS_PAINT",
        "PTS_2NDCHANCE",
        "DREB",
        "OREB",
        "REB",
        "STL",
        "FG3A",
        "FG3M",
        "TOV",
        "FG2A",
        "FG2M",
    ]

    # all stat categories that should remain as floats
    stat_categories_percentages = [
        "FG_PCT",
        "FT_PCT",
        "FG3_PCT",
        "FG2_PCT",
    ]

    expected_columns = {
        "24H": 0,
        "4H": 0,
        "7D": 0,
        "AST": 0,
        "BLK": 0,
        "BLKR": 0,
        "CS": 0,
        "DATE_MOMENT": "",
        "DATE_UPDATED_EST": "",
        "DREB": 0,
        "EDITION_STATE": "",
        "FG2A": 0,
        "FG2M": 0,
        "FG2_PCTNAME": 0,
        "FG3A": 0,
        "FG3M": 0,
        "FG3_PCT": 0,
        "FGA": 0,
        "FGM": 0,
        "FG_PCT": 0,
        "FTA": 0,
        "FTM": 0,
        "FT_PCT": 0,
        "GAME_CLOCK": "",
        "IN_PACKS": 0,
        "JERSEYNUM": 0,
        "LISTINGS": 0,
        "MIN": "PT10M01.00S",
        "MINTED": 12,
        "MINUS": -1,
        "ONCOURT": 1,
        "OPP": "",
        "OREB": 1,
        "OWNED": 1,
        "PF": 1,
        "PF_OFF": 1,
        "PFD": 1,
        "PF_TECH": 1,
        "PLAYED": 1,
        "PLAYER_ID": 1,
        "PLAY_ID": "",
        "PLUS": 1,
        "PLUS_MINUS": 1,
        "PTS_2NDCHANCE": 1,
        "PTS_PAINT": 1,
        "POSITION": "",
        "PTS": 1,
        "PTS_FASTBREAK": 1,
        "REB": 1,
        "ROOKIE_MINT": 1,
        "ROOKIE_PREMIERE": 1,
        "ROOKIE_YEAR": 1,
        "OWN_SCORE": 1,
        "OPP_SCORE": 1,
        "PERIOD": 1,
        "SET_ID": "",
        "STARTER": 1,
        "STATUS": "ACTIVE",
        "STL": 1,
        "TEAM": "LAL",
        "TOV": 1,
        "TSD": 1,
        "TS_HELD": 1,
        "TS_LINK": "",
        "UNIQUE_OWNERS": 1,
        "NAME": "Placeholder",
        "Clock": "",
    }

    otm_moment_url = "https://otmnft.com/create_moments_csv/?playerName=&setName=&team=&minprice=&maxprice=&mincirc=&maxcirc=&sortby="

    def __init__(self, topshot_data_url=otm_moment_url):
        """Creates a Stat Dataset object
        Keyword arguments:
        topshot_data_url -- str - the url for downloading topshot moment data"""

        self.topshot_data_url = topshot_data_url
        self.timezone = pytz.timezone("EST")
        # use npa_api to access live data about today's games
        self.board = scoreboard.ScoreBoard()
        self.games = self.board.games.get_dict()
        self.game_date = self.board.score_board_date
        self.now = datetime.now(tz=pytz.timezone("EST"))

        # fetching and setting up dataframes
        self.topshot_df = self.get_topshot_data(self.topshot_data_url)
        (
            self.gameday_df,
            self.todays_games,
            self.start_times,
        ) = self.get_daily_player_data()
        self.cheapest_moments = self.get_cheapest_moment(self.topshot_df)

    @st.cache
    def get_topshot_data(self, url):
        # This function downloads the moment data csv and returns a dataframe
        # r = requests.get(url, allow_redirects=True)
        # open("topshot_data.csv", "wb").write(r.content)
        topshot_df = pd.read_csv("topshot_data.csv")
        return topshot_df

    def get_cheapest_moment(self, topshot_df):
        # This function filters topshot dataframe with only cheapest moment from each player
        low_ask_filter = (
            topshot_df["Low Ask"] != 0
        )  # Low Asks = 0 -> new/unreleased moments omitted
        topshot_df = topshot_df[low_ask_filter]

        # get the indices of lowest ask moment for each player and return full filtered dataframe
        low_ask_df = (
            topshot_df[["Player Name", "Low Ask"]].groupby(["Player Name"]).idxmin()
        )
        idx_list = low_ask_df["Low Ask"].to_list()
        low_ask_df = topshot_df.loc[idx_list]

        return low_ask_df

    def get_hard_moments(self, topshot_df):
        """This function filters cheapest moment for each player in any of 
        Fandom, Rare, Legendary Tiers. If there are no moments in any of those tiers,
        it will filter the cheapest Top Shot Debut moment.
        """
        low_ask_filter = (
            topshot_df["Low Ask"] != 0
        )  # Low Asks = 0 -> new/unreleased moments omitted
        topshot_df = topshot_df[low_ask_filter]

        # Get only moments in desired tiers
        filter_tiers = (
            (topshot_df.Tier == "Fandom")
            | (topshot_df.Tier == "Rare")
            | (topshot_df.Tier == "Legendary")
        )
        only_tiers_df = topshot_df[filter_tiers]

        # Get TSD moments any players not in tier
        filter_not_tiers = ~topshot_df["Player Name"].isin(
            only_tiers_df["Player Name"].unique()
        )
        filter_tsd = topshot_df["Top Shot Debut"] == 1
        top_shot_debuts = topshot_df[filter_not_tiers][filter_tsd]

        # Combine the two filtered dataframes and get indices of lowest ask moments
        hard_df = pd.concat([only_tiers_df, top_shot_debuts])
        hard_df = hard_df[["Player Name", "Low Ask"]].groupby(["Player Name"]).idxmin()
        idx_list = hard_df["Low Ask"].to_list()
        hard_df = topshot_df.loc[idx_list]

        return hard_df[
            [
                "Player Name",
                "Set",
                "Tier",
                "Series",
                "Play",
                "Circulation Count",
                "Low Ask",
            ]
        ]

    @st.cache
    def get_daily_player_data(self):
        """
        This is the main function for retrieving and munging live data
        from nba_api requests.
        """
        # initilize lists for storing data
        daily_stats = []
        todays_games = []
        start_times = []
        team_stats = []

        # loop to get game information (teams, period, game clock, score and start time)
        for i, game in enumerate(self.games):
            away_df = get_team_stats(game["awayTeam"]["teamId"])
            home_df = get_team_stats(game["homeTeam"]["teamId"])
            game_id = game["gameId"]

            away = game["awayTeam"]["teamTricode"]
            home = game["homeTeam"]["teamTricode"]

            away_df["TEAM"] = away
            home_df["TEAM"] = home

            away_score = str(game["awayTeam"]["score"])
            home_score = str(game["homeTeam"]["score"])

            period = str(game["period"])
            game_clock = (
                game["gameClock"].replace("PT", "").replace("M", ":").replace("S", "")
            )

            start = datetime.strptime(game["gameTimeUTC"], "%Y-%m-%dT%H:%M:%S%z")
            start = start.astimezone(self.timezone)

            # Fill in lists to display store general game information
            todays_games.append(
                away
                + " at "
                + home
                + " - Q"
                + period
                + " "
                + game_clock
                + " - "
                + away_score
                + "-"
                + home_score
            )
            start_times.append(start)
            team_stats.append(away_df)
            team_stats.append(home_df)

            # If the game has already started, get the player boxscore information
            if start < self.now.astimezone(self.timezone):
                box = boxscore.BoxScore(game_id)
                time.sleep(0.2)
                away_df = pd.DataFrame(box.away_team_player_stats.get_dict())
                home_df = pd.DataFrame(box.home_team_player_stats.get_dict())

                # Store stats for away team players
                away_df = away_df.join(
                    pd.DataFrame((away_df.pop("statistics").values.tolist()))
                )
                away_df["Team"] = away
                away_df["Opp"] = home
                away_df["OWN_SCORE"] = away_score
                away_df["OPP_SCORE"] = home_score
                away_df["Clock"] = game_clock
                if game["gameStatusText"] != "Final":
                    away_df["Period"] = period
                else:
                    away_df["Period"] = 0

                # Store stats for home team players
                home_df = home_df.join(
                    pd.DataFrame((home_df.pop("statistics").values.tolist()))
                )
                home_df["Team"] = home
                home_df["Opp"] = away
                home_df["OWN_SCORE"] = home_score
                home_df["OPP_SCORE"] = away_score
                home_df["Clock"] = game_clock
                if game["gameStatusText"] != "Final":
                    home_df["Period"] = period
                else:
                    home_df["Period"] = 0

                # store these stats in daily stats list
                daily_stats.append(away_df)
                daily_stats.append(home_df)

        start_times.sort()
        first_start = start_times[0]
        if first_start < self.now.astimezone(self.timezone):
            daily_stats_df = pd.concat(daily_stats)
            daily_stats_df.drop(
                columns=[
                    "nameI",
                    "firstName",
                    "familyName",
                    "order",
                    "minutesCalculated",
                ],
                inplace=True,
            )
            daily_stats_df.rename(
                columns={
                    "assists": "ast",
                    "blocks": "blk",
                    "blocksReceived": "blkr",
                    "fieldGoalsAttempted": "fga",
                    "fieldGoalsMade": "fgm",
                    "fieldGoalsPercentage": "fg_pct",
                    "foulsOffensive": "PF_Off",
                    "foulsdrawn": "PFD",
                    "foulsPersonal": "PF",
                    "foulsTechnical": "PF_Tech",
                    "freeThrowsAttempted": "FTA",
                    "freeThrowsMade": "FTM",
                    "freeThrowsPercentage": "FT_PCT",
                    "minus": "minus",
                    "minutes": "min",
                    "plus": "plus",
                    "plusMinusPoints": "PLUS_MINUS",
                    "points": "pts",
                    "pointsFastBreak": "pts_fastbreak",
                    "pointsInThePaint": "pts_paint",
                    "pointsSecondChance": "pts_2ndchance",
                    "reboundsDefensive": "DREB",
                    "reboundsOffensive": "OREB",
                    "reboundsTotal": "REB",
                    "steals": "STL",
                    "threePointersAttempted": "FG3A",
                    "threePointersMade": "FG3M",
                    "threePointersPercentage": "FG3_PCT",
                    "turnovers": "TOV",
                    "twoPointersAttempted": "FG2A",
                    "twoPointersMade": "FG2M",
                    "twoPointersPercentage": "FG2_PCT",
                    "name": "name",
                    "status": "status",
                    "personId": "player_ID",
                    "jerseyNum": "jerseyNum",
                    "position": "position",
                    "starter": "starter",
                    "oncourt": "oncourt",
                    "played": "played",
                    "team": "team",
                    "Opp": "OPP",
                    "Game_Clock": "Game_Clock",
                },
                inplace=True,
            )
            daily_stats_df.columns = daily_stats_df.columns.str.upper()
            daily_stats_df.set_index(["NAME", "TEAM"], inplace=True)
            season_stats_df = pd.concat(team_stats)
            season_stats_df.set_index(["NAME", "TEAM"], inplace=True)
            daily_stats_df = season_stats_df.join(
                daily_stats_df, on=["NAME", "TEAM"], lsuffix="_avg", rsuffix="",
            )
            daily_stats_df.reset_index(inplace=True)

        else:
            daily_stats_df = pd.DataFrame(self.expected_columns, index=["NAME", "TEAM"])
            season_stats_df = pd.concat(team_stats)
            daily_stats_df = season_stats_df.set_index(["NAME", "TEAM"]).join(
                daily_stats_df.set_index(["NAME", "TEAM"]),
                on=["NAME", "TEAM"],
                lsuffix="_avg",
                rsuffix="",
            )
            daily_stats_df.reset_index(inplace=True)

        ts_raw_data = self.topshot_df
        topshot_data_cheap = self.get_cheapest_moment(ts_raw_data)
        topshot_data_hard = self.get_hard_moments(ts_raw_data)

        topshot_data_cheap.rename(columns={"Player Name": "NAME"}, inplace=True)
        topshot_data_hard.rename(columns={"Player Name": "NAME"}, inplace=True)

        topshot_data = topshot_data_cheap.set_index("NAME").join(
            topshot_data_hard.set_index("NAME"),
            on="NAME",
            lsuffix="_easy",
            rsuffix="_hard",
        )
        topshot_data.reset_index(inplace=True)
        topshot_data.NAME = (
            topshot_data.NAME.str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
        )
        topshot_data.NAME.astype(str)
        topshot_data.rename(
            columns={
                "Time Stamp (EST)": "date_updated_EST",
                "Set_easy": "Set_easy",
                "Tier_easy": "Tier_easy",
                "Series_easy": "Series_easy",
                "Play_easy": "Play_easy",
                "Date of Moment": "date_moment",
                "Team": "Team",
                "Circulation Count_easy": "Count_easy",
                "Owned": "Owned",
                "Unique Owners": "Unique_Owners",
                "In Packs": "In_Packs",
                "Minted": "Minted",
                "Held by TS": "TS_held",
                "Collector Score": "cs",
                "Low Ask_easy": "Low_Ask_easy",
                "4h": "4h",
                "24h": "24h",
                "7d": "7d",
                "Listings": "Listings",
                "Top Shot Debut": "tsd",
                "Rookie Premiere": "rookie_premiere",
                "Rookie Mint": "rookie_mint",
                "Rookie Year": "rookie_year",
                "Edition State": "Edition_State",
                "Play ID": "Play_ID",
                "Set ID": "Set_ID",
                "Top Shot Link": "Ts_Link",
                "Set_hard": "Set_hard",
                "Tier_hard": "Tier_hard",
                "Series_hard": "Series_hard",
                "Play_hard": "Play_hard",
                "Circulation Count_hard": "Count_hard",
                "Low Ask_hard": "Low_Ask_hard",
            },
            inplace=True,
        )
        topshot_data.columns = topshot_data.columns.str.upper()
        # Player specific fixes for discrepancies bewteen nba_api name and topshot name
        topshot_data.NAME[topshot_data.NAME == "Marcus Morris"] = "Marcus Morris Sr."
        topshot_data.NAME[topshot_data.NAME == "Enes Kanter"] = "Enes Freedom"
        topshot_data.NAME[topshot_data.NAME == "Steph Curry"] = "Stephen Curry"

        # join topshot data and nba stats data with "name" as the key
        daily_stats_df.set_index("NAME", inplace=True)
        topshot_data.set_index("NAME", inplace=True)
        daily_stats_df = daily_stats_df.join(
            topshot_data, on="NAME", lsuffix="_nba", rsuffix="_TS"
        )
        # convert all column names to UPPERCASE and rename longer ones
        daily_stats_df.columns = daily_stats_df.columns.str.upper()

        # format player minutes to be more readable
        def time_to_float(df):
            df["MIN"] = df["MIN"].fillna("PT00M00.00S")
            time = (
                df["MIN"]
                .str.replace("PT", "", regex=True)
                .str.replace("S", "", regex=True)
                .str.split("M", expand=True)
            )
            time = time.astype(float)
            df["MIN"] = time[0] + (time[1] / 60)

        time_to_float(daily_stats_df)

        # convert topshot data columns to integers then strings
        col_list = ["COUNT_EASY", "LOW_ASK_EASY", "COUNT_HARD", "LOW_ASK_HARD"]
        for col in col_list:
            daily_stats_df[col] = daily_stats_df[col].fillna(-1)
            daily_stats_df[col] = daily_stats_df[col].astype(int)
            daily_stats_df[col] = daily_stats_df[col].astype(str)
            daily_stats_df[col] = daily_stats_df[col].replace("-1", np.nan)

        # convert integers stat categories from float -> int so we can add/subtract
        for col in self.stat_categories_integer:
            col = col.upper()
            daily_stats_df[col] = daily_stats_df[col].fillna(0)
            daily_stats_df[col] = daily_stats_df[col].astype(int)

        daily_stats_df["OWN_SCORE"] = daily_stats_df["OWN_SCORE"].fillna(0).astype(int)
        daily_stats_df["OPP_SCORE"] = daily_stats_df["OPP_SCORE"].fillna(0).astype(int)
        daily_stats_df["DIFFERENTIAL"] = (
            daily_stats_df["OWN_SCORE"] - daily_stats_df["OPP_SCORE"]
        )
        daily_stats_df.rename(columns={"TEAM_NBA": "TEAM"}, inplace=True)
        daily_stats_df.reset_index(inplace=True)
        daily_stats_df.set_index(["NAME", "TEAM"], inplace=True)

        return daily_stats_df, todays_games, start_times
