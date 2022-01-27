class WebAppParameters:
    CHALLENGE_NOW = False
    NUM_HIGHLIGHTED = 10
    CHALLENGE_CATS = ["ftm"]
    DEFAULT_STAT_CATS = ["pts", "reb", "ast", "stl", "blk", "tov"]
    DEFAULT_CATS = ["score", "game_status", "min", "on_court"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    LOGO_PATH = "frontend/nba_logo.png"
    AUTO_REFRESH_INTERVAL = 60000  # 1 minute
    AUTO_REFRESH_LIMIT = 120
    CSS_PATH = "frontend/css/streamlit.css"
    IMPORT_ADDITIONAL_DAY = False
    ADDITIONAL_DAY_PATH = "prevgamedays/2022-01-2122_NBAStats_edited.csv"
