from data_fetchers.live.utils import get_live_stats, clean_live_stats


class LiveStats:
    def __init__(self, todays_games):
        self.todays_games = todays_games
        self.daily_stats_df, self.now = get_live_stats(todays_games)
        clean_live_stats(self.daily_stats_df)
        self.daily_stats_df.columns = self.daily_stats_df.columns.str.lower()
