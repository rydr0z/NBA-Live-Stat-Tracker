from data_combine.utils import combine_data, clean_and_create_columns
from data_fetchers.live.livestatfetcher import LiveStats
from data_fetchers.season.seasonstatfetcher import SeasonStats
from data_fetchers.todaysgames.todaysgamesfetcher import TodaysGames
from data_fetchers.topshot.topshotfetcher import TopShotData


class CombinedStats:
    def __init__(self):
        tg = TodaysGames()
        self.todays_games = tg.todays_games
        self.date = tg.date
        ls = LiveStats(todays_games=self.todays_games)
        ss = SeasonStats(todays_games=self.todays_games)
        td = TopShotData()
        self.daily_stats_df = ls.daily_stats_df
        self.now = ls.now
        self.season_stats_df = ss.season_stats_df
        self.topshot_data = td.topshot_data

        self.stats = combine_data(
            self.todays_games,
            self.daily_stats_df,
            self.season_stats_df,
            self.topshot_data,
        )

        clean_and_create_columns(self.stats)

