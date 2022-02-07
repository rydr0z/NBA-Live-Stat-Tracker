from data_combine.utils import combine_data, clean_and_create_columns
from data_fetchers.injuries.injuryreport import InjuryReport
from data_fetchers.live.livestatfetcher import LiveStats
from data_fetchers.season.seasonstatfetcher import SeasonStats
from data_fetchers.todaysgames.todaysgamesfetcher import TodaysGames
from data_fetchers.topshot.topshotfetcher import TopShotData


class CombinedStats:

    def __init__(self, games_df=None, date=None, last_n_games=0):
        tg = TodaysGames()
        self.todays_games_df = tg.todays_games
        self.date = tg.date
        ls = LiveStats(todays_games=self.todays_games_df)
        ss = SeasonStats(todays_games=self.todays_games_df, games_df=games_df, date=date, last_n_games=last_n_games)
        td = TopShotData()
        ir = InjuryReport()
        self.daily_stats_df = ls.daily_stats_df
        self.now = ls.now
        self.season_stats_df = ss.season_stats_df
        self.topshot_data_df = td.topshot_data
        self.injury_report_df = ir.injury_report_df
        self.additional_stats_df = ss.stats_since_df
        self.stats = combine_data(
            self.todays_games_df,
            self.daily_stats_df,
            self.season_stats_df,
            self.topshot_data_df,
            self.injury_report_df,
            self.additional_stats_df
        )
        clean_and_create_columns(self.stats)
