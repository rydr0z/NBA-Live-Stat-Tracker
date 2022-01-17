import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
import numpy as np

from nba_api.live.nba.endpoints import scoreboard
from nba_api.live.nba.endpoints import boxscore

def remove_accents(a):
    return unidecode.unidecode(a.decode('utf-8'))
    
class Stat_Dataset:
    
    stat_categories_integer = [
        'assists', 'blocks', 'blocksReceived', 'fieldGoalsAttempted', 'fieldGoalsMade', 
        'foulsOffensive', 'foulsDrawn', 'foulsPersonal', 'foulsTechnical', 
        'freeThrowsAttempted', 'freeThrowsMade', 'minus', 'plus', 'plusMinusPoints', 'points', 'pointsFastBreak',
        'pointsInThePaint', 'pointsSecondChance', 
        'reboundsDefensive', 'reboundsOffensive', 'reboundsTotal', 'steals', 'threePointersAttempted', 
        'threePointersMade', 'turnovers', 'twoPointersAttempted', 'twoPointersMade']

    stat_categories_percentages = [
        'fieldGoalsPercentage', 'freeThrowsPercentage','threePointersPercentage','twoPointersPercentage'
    ]

       # class variable shared by all instances

    def __init__(self, topshot_data_path):
        self.topshot_data_path = topshot_data_path
        self.board = scoreboard.ScoreBoard()
        self.timezone = pytz.timezone('EST')
        self.games = self.board.games.get_dict()
        self.game_date = self.board.score_board_date

        self.topshot_df = self.get_topshot_data(self.topshot_data_path)
        self.gameday_df, self.todays_games, self.start_times = self.get_daily_player_data()
        self.highest_circs = self.get_highest_circ_low_ask(self.topshot_df)
        


    def get_topshot_data(self, path):
        topshot_df = pd.read_csv(path)
        return topshot_df

    def get_highest_circ_low_ask(self, topshot_df):
        max_circ = topshot_df[['Player Name', 'Circulation Count']].groupby(['Player Name']).idxmax()
        idx_list = max_circ['Circulation Count'].to_list()
        high_circ_low_ask_df = topshot_df.loc[idx_list]
        return high_circ_low_ask_df

    def get_daily_player_data(self):
        now = datetime.now(tz=pytz.timezone('EST'))
        daily_stats = []
        todays_games = []
        start_times = []
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
            todays_games.append(away+' at '+home+' - Q'+period+' '+game_clock+' - '+away_score+'-'+home_score)
            start_times.append(start.strftime("%H:%M:%S"))

            if start < now:
                box = boxscore.BoxScore(game_id)
                away_df = pd.DataFrame(box.away_team_player_stats.get_dict())
                home_df = pd.DataFrame(box.home_team_player_stats.get_dict())
                away_df_stats = away_df.join(pd.DataFrame(
                    (away_df.pop('statistics').values.tolist())))
                away_df_stats['Team'] = away
                away_df_stats['Opponent'] = home
                away_df_stats['Score'] = away_score + '-' + home_score
                if game['gameStatusText'] != 'Final':
                    away_df_stats['Game Clock'] = 'Q' + period + ' - ' + game_clock
                else:
                    away_df_stats['Game Clock'] = 'Final'
                home_df_stats = home_df.join(pd.DataFrame(
                    (home_df.pop('statistics').values.tolist())))
                home_df_stats['Team'] = home
                home_df_stats['Opponent'] = away
                home_df_stats['Score'] = home_score + '-' + away_score
                if game['gameStatusText'] != 'Final':
                    home_df_stats['Game Clock'] = 'Q' + period + ' - ' + game_clock
                else:
                    home_df_stats['Game Clock'] = 'Final'
                daily_stats.append(away_df_stats)
                daily_stats.append(home_df_stats)

        daily_stats_df = pd.concat(daily_stats)
        ts_raw_data = self.topshot_df
        topshot_data = self.get_highest_circ_low_ask(ts_raw_data)
        topshot_data.rename(columns={'Player Name':'name'}, inplace=True)
        topshot_data.name = topshot_data.name.str.normalize('NFKD').str.encode('ascii',errors='ignore').str.decode('utf-8')
        topshot_data.name.astype(str)

        daily_stats_df = daily_stats_df.set_index('name').join(topshot_data.set_index('name'), on='name', lsuffix='_NBA', rsuffix='_TS')
        daily_stats_df.columns = daily_stats_df.columns.str.upper()
        daily_stats_df.rename(columns={
            'TEAM_NBA':'TEAM',
            'CIRCULATION COUNT':'COUNT'}, inplace=True)

        daily_stats_df['MINUTES'] = daily_stats_df['MINUTES'].replace('PT','',regex=True).replace('M',':',regex=True).replace('S','',regex=True)

        col_list = ['COUNT', 'LOW ASK']
        for col in col_list:
            daily_stats_df[col] = daily_stats_df[col].fillna(-1)
            daily_stats_df[col] = daily_stats_df[col].astype(int)
            daily_stats_df[col] = daily_stats_df[col].astype(str)
            daily_stats_df[col] = daily_stats_df[col].replace('-1', np.nan)

        for col in self.stat_categories_integer:
            col=col.upper()
            daily_stats_df[col] = daily_stats_df[col].astype(int)

        return daily_stats_df, todays_games, start_times
