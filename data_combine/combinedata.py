from data_combine.utils import combine_data, clean_and_create_columns
from data_fetchers.live.livestatfetcher import LiveStats
from data_fetchers.season.seasonstatfetcher import SeasonStats
from data_fetchers.todaysgames.todaysgamesfetcher import TodaysGames
from data_fetchers.topshot.topshotfetcher import TopShotData
from data_fetchers.injuries.injuryreport import InjuryReport


class CombinedStats:

    def __init__(self):
        tg = TodaysGames()
        self.todays_games_df = tg.todays_games
        self.date = tg.date
        self.games_df, self.date_prev = tg.get_games_on_date(2022, 1, 28)
        ls = LiveStats(todays_games=self.todays_games_df)
        ss = SeasonStats(todays_games=self.todays_games_df, games_df=self.games_df, date=self.date_prev)
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
