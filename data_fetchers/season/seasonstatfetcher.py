from data_fetchers.season.utils import get_season_stats


class SeasonStats:
    def __init__(self, todays_games):
        self.season_stats_df = get_season_stats(todays_games)
        self.season_stats_df.columns = self.season_stats_df.columns.str.lower()
