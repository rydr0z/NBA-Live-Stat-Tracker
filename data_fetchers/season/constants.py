from nba_api.stats.library.parameters import GameDate


class SeasonParameters:
    COLUMNS_TO_AVG = [
        "AST",
        "BLK",
        "BLKA",
        "DREB",
        "FG3A",
        "FG3M",
        "FGA",
        "FGM",
        "FTA",
        "FTM",
        "MIN",
        "OREB",
        "PF",
        "PFD",
        "PTS",
        "REB",
        "STL",
        "TOV",
    ]

    COLUMNS_TO_DROP = [
        "AST_RANK",
        "BLKA_RANK",
        "BLK_RANK",
        "DD2_RANK",
        "DREB_RANK",
        "FG3A_RANK",
        "FG3M_RANK",
        "FG3_PCT_RANK",
        "FGA_RANK",
        "FGM_RANK",
        "FG_PCT_RANK",
        "FTA_RANK",
        "FTM_RANK",
        "FT_PCT_RANK",
        "GP_RANK",
        "GROUP_SET",
        "L_RANK",
        "MIN_RANK",
        "NBA_FANTASY_PTS",
        "NBA_FANTASY_PTS_RANK",
        "NICKNAME",
        "OREB_RANK",
        "PFD_RANK",
        "PF_RANK",
        "PLUS_MINUS_RANK",
        "PTS_RANK",
        "REB_RANK",
        "STL_RANK",
        "TD3_RANK",
        "TOV_RANK",
        "W_PCT_RANK",
        "W_RANK",
    ]

    HEADERS = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://stats.nba.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true'
    }
    SLEEP_INTERVAL = 1
    GAME_DATE_OBJECT = GameDate()
    START_DATE = GAME_DATE_OBJECT.get_date(2021, 10, 18)
    END_DATE = GAME_DATE_OBJECT.default
    TIMEOUT = 100
