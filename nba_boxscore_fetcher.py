import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
import numpy as np

from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import boxscore
    
class Stat_Dataset:
    
    # all stat categories that can be converted to int later on
    stat_categories_integer = [
        'assists', 'blocks', 'blocksReceived', 'fieldGoalsAttempted', 'fieldGoalsMade', 
        'foulsOffensive', 'foulsDrawn', 'foulsPersonal', 'foulsTechnical', 
        'freeThrowsAttempted', 'freeThrowsMade', 'minus', 'plus', 'plusMinusPoints', 'points', 'pointsFastBreak',
        'pointsInThePaint', 'pointsSecondChance', 
        'reboundsDefensive', 'reboundsOffensive', 'reboundsTotal', 'steals', 'threePointersAttempted', 
        'threePointersMade', 'turnovers', 'twoPointersAttempted', 'twoPointersMade']

    # all stat categories that should remain as floats
    stat_categories_percentages = [
        'fieldGoalsPercentage', 'freeThrowsPercentage','threePointersPercentage','twoPointersPercentage'
    ]

    otm_moment_url = "https://otmnft.com/create_moments_csv/?playerName=&setName=&team=&minprice=&maxprice=&mincirc=&maxcirc=&sortby="

    def __init__(self, topshot_data_url=otm_moment_url):
        """Creates a Stat Dataset object
        Keyword arguments:
        topshot_data_url -- str - the url for downloading topshot moment data"""
        
        self.topshot_data_url = topshot_data_url
        self.timezone = pytz.timezone('EST')
        # use npa_api to access live data about today's games
        self.board = scoreboard.ScoreBoard()
        self.games = self.board.games.get_dict()
        self.game_date = self.board.score_board_date
        

        # fetching and setting up dataframes
        self.topshot_df = self.get_topshot_data(self.topshot_data_url)
        self.gameday_df, self.todays_games, self.start_times = self.get_daily_player_data()
        self.cheapest_moments = self.get_cheapest_moment(self.topshot_df)
        

    @st.cache
    def get_topshot_data(self, url):
        # This function downloads the moment data csv and returns a dataframe
        r = requests.get(url, allow_redirects=True)
        open('topshot_data.csv', 'wb').write(r.content)
        topshot_df = pd.read_csv('topshot_data.csv')
        return topshot_df

    @st.cache
    def get_cheapest_moment(self, topshot_df):
        # This function filters topshot dataframe with only cheapest moment from each player
        low_ask_filter = topshot_df['Low Ask']!=0 # Low Asks = 0 -> new/unreleased moments omitted
        topshot_df = topshot_df[low_ask_filter]

        # get the indices of lowest ask moment for each player and return full filtered dataframe
        low_ask_df = topshot_df[['Player Name', 'Low Ask']].groupby(['Player Name']).idxmin()
        idx_list = low_ask_df['Low Ask'].to_list()
        low_ask_df = topshot_df.loc[idx_list]

        return low_ask_df

    @st.cache
    def get_hard_moments(self, topshot_df):
        """This function filters cheapest moment for each player in any of 
        Fandom, Rare, Legendary Tiers. If there are no moments in any of those tiers,
        it will filter the cheapest Top Shot Debut moment.
        """
        low_ask_filter = topshot_df['Low Ask']!=0 # Low Asks = 0 -> new/unreleased moments omitted
        topshot_df = topshot_df[low_ask_filter]

        # Get only moments in desired tiers
        filter_tiers = (topshot_df.Tier=='Fandom') | (topshot_df.Tier=='Rare') | (topshot_df.Tier=='Legendary')
        only_tiers_df = topshot_df[filter_tiers]

        # Get TSD moments any players not in tier
        filter_not_tiers = ~topshot_df['Player Name'].isin(only_tiers_df['Player Name'].unique())
        filter_tsd = topshot_df['Top Shot Debut'] == 1
        top_shot_debuts = topshot_df[filter_not_tiers][filter_tsd]

        # Combine the two filtered dataframes and get indices of lowest ask moments
        hard_df = pd.concat([only_tiers_df, top_shot_debuts])
        hard_df = hard_df[['Player Name', 'Low Ask']].groupby(['Player Name']).idxmin()
        idx_list = hard_df['Low Ask'].to_list()
        hard_df = topshot_df.loc[idx_list]

        return hard_df[['Player Name','Set','Tier','Series','Play','Circulation Count','Low Ask']]

    def get_daily_player_data(self):
        """
        This is the main function for retrieving and munging live data
        from nba_api requests.
        """
        now = datetime.now(tz=pytz.timezone('EST'))

        # initilize lists for storing data
        daily_stats = []
        todays_games = []
        start_times = []

        # loop to get game information (teams, period, game clock, score and start time)
        for i, game in enumerate(self.games):
            game_id = game['gameId']

            away = game['awayTeam']['teamTricode']
            home = game['homeTeam']['teamTricode']

            away_score = str(game['awayTeam']['score'])
            home_score = str(game['homeTeam']['score'])

            period = str(game['period'])
            game_clock = game['gameClock'].replace('PT','').replace('M',':').replace('S','')
            
            start = datetime.strptime(
                game['gameTimeUTC'], '%Y-%m-%dT%H:%M:%S%z')
            start = start.astimezone(self.timezone)

            # Fill in lists to display store general game information
            todays_games.append(away+' at '+home+' - Q'+period+' '+game_clock+' - '+away_score+'-'+home_score)
            start_times.append(start.strftime("%H:%M:%S"))

            # If the game has already started, get the player boxscore information
            if start < now:
                box = boxscore.BoxScore(game_id)

                away_df = pd.DataFrame(box.away_team_player_stats.get_dict())
                home_df = pd.DataFrame(box.home_team_player_stats.get_dict())

                # Store stats for away team players
                away_df_stats = away_df.join(pd.DataFrame(
                    (away_df.pop('statistics').values.tolist())))
                away_df_stats['Team'] = away
                away_df_stats['Opponent'] = home
                away_df_stats['Score'] = away_score + '-' + home_score
                if game['gameStatusText'] != 'Final':
                    away_df_stats['Game Clock'] = 'Q' + period + ' - ' + game_clock
                else:
                    away_df_stats['Game Clock'] = 'Final'
                
                # Store stats for home team players
                home_df_stats = home_df.join(pd.DataFrame(
                    (home_df.pop('statistics').values.tolist())))
                home_df_stats['Team'] = home
                home_df_stats['Opponent'] = away
                home_df_stats['Score'] = home_score + '-' + away_score
                if game['gameStatusText'] != 'Final':
                    home_df_stats['Game Clock'] = 'Q' + period + ' - ' + game_clock
                else:
                    home_df_stats['Game Clock'] = 'Final'
                
                # store these stats in daily stats list
                daily_stats.append(away_df_stats)
                daily_stats.append(home_df_stats)

        # combine all player stats into one dataframe
        daily_stats_df = pd.concat(daily_stats)

        # join cheap and hard moment data with "Player Name" as the key
        ts_raw_data = self.topshot_df
        topshot_data_cheap = self.get_cheapest_moment(ts_raw_data)
        topshot_data_hard = self.get_hard_moments(ts_raw_data)

        topshot_data_cheap.rename(columns={'Player Name':'name'}, inplace=True)
        topshot_data_hard.rename(columns={'Player Name':'name'}, inplace=True)

        topshot_data = topshot_data_cheap.set_index('name').join(topshot_data_hard.set_index('name'), on='name', lsuffix='_easy', rsuffix='_hard')
        topshot_data.reset_index(inplace=True)
        topshot_data.name = topshot_data.name.str.normalize('NFKD').str.encode('ascii',errors='ignore').str.decode('utf-8')
        topshot_data.name.astype(str)

        # Player specific fixes for discrepancies bewteen nba_api name and topshot name
        topshot_data.name[topshot_data.name == "Marcus Morris"] = "Marcus Morris Sr."
        topshot_data.name[topshot_data.name == "Enes Kanter"] = "Enes Freedom"

        # join topshot data and nba stats data with "name" as the key
        daily_stats_df = daily_stats_df.set_index('name').join(topshot_data.set_index('name'), on='name', lsuffix='_NBA', rsuffix='_TS')
        
        # convert all column names to UPPERCASE and rename longer ones
        daily_stats_df.columns = daily_stats_df.columns.str.upper()
        daily_stats_df.rename(columns={
            'CIRCULATION COUNT_EASY':'COUNT_EASY',
            'CIRCULATION COUNT_HARD':'COUNT_HARD'}, inplace=True)

        # format player minutes to be more readable
        daily_stats_df['MINUTES'] = daily_stats_df['MINUTES'].replace('PT','',regex=True).replace('M',':',regex=True).replace('S','',regex=True)

        # convert topshot data columns to integers then strings
        col_list = ['COUNT_EASY', 'LOW ASK_EASY', 'COUNT_HARD', 'LOW ASK_HARD']
        for col in col_list:
            daily_stats_df[col] = daily_stats_df[col].fillna(-1)
            daily_stats_df[col] = daily_stats_df[col].astype(int)
            daily_stats_df[col] = daily_stats_df[col].astype(str)
            daily_stats_df[col] = daily_stats_df[col].replace('-1', np.nan)

        # convert integers stat categories from float -> int so we can add/subtract
        for col in self.stat_categories_integer:
            col=col.upper()
            daily_stats_df[col] = daily_stats_df[col].astype(int)

        return daily_stats_df, todays_games, start_times
