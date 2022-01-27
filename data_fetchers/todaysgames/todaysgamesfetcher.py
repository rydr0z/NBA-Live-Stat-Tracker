from data_fetchers.todaysgames.utils import get_todays_games


class TodaysGames:
    def __init__(self):
        self.todays_games, self.date = get_todays_games()
