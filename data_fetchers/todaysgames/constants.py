import pytz


class TodayParameters:
    DEFAULT_COLS = [
        "away_id",
        "away_score",
        "away_team",
        "game_clock",
        "game_id",
        "game_status",
        "home_id",
        "home_score",
        "home_team",
        "period",
        "start_time",
    ]

    TIMEZONE = pytz.timezone("EST")
