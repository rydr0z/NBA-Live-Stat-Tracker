class WebAppParameters:
    AUTO_REFRESH_INTERVAL = 60000  # 1 minute
    AUTO_REFRESH_LIMIT = 120
    ADDITIONAL_DAY_PATH = "prevgamedays/2022-01-2122_NBAStats_edited.csv"
    CHALLENGE_CATS = "ast"
    CHALLENGE_NOW = True
    CHALLENGE_NAME = "Flash Challenge: 'Join Forces' "
    CHALLENGE_DESC_EASY = "Six Moments must be Series 1 or Series 2 Moments from the team with more assists in each" \
                          " NBA game played on Thursday, Feb. 3. If the teams tie in assists, you need a Moment from" \
                          " the team that won the game. Four Moments must be Series 1 or Series 2 Moments from the" \
                          " four players with the most assists from NBA games played on Thursday, Feb. 3. If a player" \
                          " does not have a Series 1 or Series 2 Moment, you need their Top Shot Debut. If any of" \
                          " the players don't have a Moment on NBA Top Shot at the start of the Flash Challenge, then" \
                          " the player with the fifth most assists will be needed and so on."
    CHALLENGE_DESC_HARD = None
    CSS_PATH = "frontend/css/streamlit.css"
    DEFAULT_CATS = ["score", "game_status", "min", "on_court"]
    DEFAULT_STAT_CATS = ["pts", "reb", "ast", "stl", "blk", "tov"]
    FILE_NAME_SAVE = "_NBAStats.csv"
    IMPORT_ADDITIONAL_DAY = False
    LOGO_PATH = "frontend/nba_logo.png"
    NUM_HIGHLIGHTED = 4
    PATH_SAVE = "data/prevgamedays/"
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
    TOP_STATS_OVERALL = True
    TOP_STATS_PER_GAME = False
