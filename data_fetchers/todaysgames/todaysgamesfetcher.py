from data_fetchers.todaysgames.utils import get_todays_games, get_games_on_date


class TodaysGames:
    def __init__(self):
        self.todays_games, self.date = get_todays_games()

    def get_games_on_date(self, year, month, day):
        return get_games_on_date(year, month, day)