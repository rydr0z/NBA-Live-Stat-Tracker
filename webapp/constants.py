class WebAppParameters:
    AUTO_REFRESH_INTERVAL = 60000  # 1 minute
    AUTO_REFRESH_LIMIT = 120
    ADDITIONAL_DAY_PATH = "prevgamedays/2022-01-2122_NBAStats_edited.csv"
    CHALLENGE_CATS = ["pts", "reb", "ast"]
    CHALLENGE_NOW = True
    CHALLENGE_NAME = "Flash Challenge: 'Day by Day' "
    CHALLENGE_DESC_EASY = "Create a Challenge Entry with exactly nine (9) Moment™ NFTs. The nine Moments include: 3 " \
                          "Moments from the players that lead in points each day on Friday, Saturday and Sunday; 3 " \
                          "Moments from the players that lead in rebounds each day on Friday, Saturday and Sunday; 3 " \
                          "Moments from the players that lead in assists each day on Friday, Saturday and Sunday. " \
                          "These Moments must be Series 1 or Series 2 Moments. If the player does not have a Series 1 " \
                          "or Series 2 Moment then you must use their Top Shot Debut. "

    CHALLENGE_DESC_HARD = None
    CSS_PATH = "frontend/css/streamlit.css"
    DEFAULT_CATS = ["score", "game_status", "min", "on_court"]
    DEFAULT_STAT_CATS = ["pts", "reb", "ast", "stl", "blk", "tov"]
    FILE_NAME_SAVE = "_NBAStats.csv"
    IMPORT_ADDITIONAL_DAY = False
    LOGO_PATH = "frontend/nba_logo.png"
    NUM_HIGHLIGHTED = 1
    PATH_SAVE = "data/prevgamedays/"
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
    TOP_STATS_OVERALL = True
    TOP_STATS_PER_GAME = False
