from data_fetchers.season.utils import get_season_stats, get_stats_since


class SeasonStats:
    def __init__(self, todays_games, games_df=None, date=None, last_n_games=0):
        self.season_stats_df = get_season_stats(todays_games, last_n_games=last_n_games)
        self.season_stats_df.columns = self.season_stats_df.columns.str.lower()
        if games_df is not None:
            self.stats_since_df = get_stats_since(games_df, date)
            self.stats_since_df.columns = self.stats_since_df.columns.str.lower()
        else:
            self.stats_since_df = None
