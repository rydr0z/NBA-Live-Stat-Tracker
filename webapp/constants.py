class WebAppParameters:
    AUTO_REFRESH_INTERVAL = 60000  # 1 minute
    AUTO_REFRESH_LIMIT = 120
    ADDITIONAL_DAY_PATH = "prevgamedays/2022-01-2122_NBAStats_edited.csv"
    CHALLENGE_CATS = "fgm+ftm"
    CHALLENGE_NOW = True
    CHALLENGE_NAME = "Flash Challenge: 'Takeover' "
    CHALLENGE_DESC_EASY = "Easy Flash: Create a challenge entry with any Moment of the top player in each game tonight, " \
                          "February 2, 2022, in most combined Free throws made & Field Goals Made."
    CHALLENGE_DESC_HARD = "Hard Flash: Create a challenge entry with a Top Shot Debut Moment of the top player in each" \
                          " game tonight, February 2, 2022, in most combined Free Throws made & Field Goals Made. " \
                          "OR you may use Luka Dončić and/or LaMelo Ball Cool Cats Moments in any or all slots."
    CSS_PATH = "frontend/css/streamlit.css"
    DEFAULT_CATS = ["score", "game_status", "injury_status", "min", "on_court"]
    DEFAULT_STAT_CATS = ["pts", "reb", "ast", "stl", "blk", "tov"]
    FILE_NAME_SAVE = "_NBAStats.csv"
    IMPORT_ADDITIONAL_DAY = False
    LOGO_PATH = "frontend/nba_logo.png"
    NUM_HIGHLIGHTED = 0
    PATH_SAVE = "data/prevgamedays/"
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
