import pandas as pd
import pytz
from nba_api.stats.library.parameters import GameDate


class CombinedParameters:
    COLUMNS_TO_RENAME = {
        "team_nba": "team",
    }
    STAT_CATEGORIES_INTEGER = [
        "ast",
        "blk",
        "blkr",
        "dreb",
        "fg2a",
        "fg2m",
        "fg3a",
        "fg3m",
        "fga",
        "fgm",
        "fta",
        "ftm",
        "minus",
        "oreb",
        "pf",
        "pfd",
        "pfoff",
        "pftech",
        "plus",
        "plus_minus",
        "pts",
        "pts_2nd_chance",
        "pts_fastbreak",
        "pts_paint",
        "reb",
        "stl",
        "tov",
    ]
    NA_COLUMNS_TO_FILL = ["on_court", "easy_moment", "count_easy", "4hchange_easy", "low_ask_easy", "hard_moment",
                          "count_hard", "4hchange_hard", "low_ask_hard"]


class InjuriesParameters:
    URL = "https://www.cbssports.com/nba/injuries/"
    REPLACE_STR = {"Expected to be out until at least": "INJ - ",
                   "Out for the season": "OUT",
                   "Game Time Decision": "GTD"}


class LiveParameters:
    COLUMNS_TO_DROP = ["nameI", "firstName", "familyName", "order", "minutesCalculated"]
    COLUMNS_TO_RENAME = {
        "assists": "ast",
        "blocks": "blk",
        "blocksReceived": "blkr",
        "fieldGoalsAttempted": "fga",
        "fieldGoalsMade": "fgm",
        "fieldGoalsPercentage": "fg_pct",
        "foulsOffensive": "pfoff",
        "foulsdrawn": "pfd",
        "foulsPersonal": "pf",
        "foulsTechnical": "pftech",
        "freeThrowsAttempted": "fta",
        "freeThrowsMade": "ftm",
        "freeThrowsPercentage": "ft_pct",
        "minus": "minus",
        "minutes": "min",
        "plus": "plus",
        "plusMinusPoints": "plus_minus",
        "points": "pts",
        "pointsFastBreak": "pts_fastbreak",
        "pointsInThePaint": "pts_paint",
        "pointsSecondChance": "pts_2nd_chance",
        "reboundsDefensive": "dreb",
        "reboundsOffensive": "oreb",
        "reboundsTotal": "reb",
        "steals": "stl",
        "threePointersAttempted": "fg3a",
        "threePointersMade": "fg3m",
        "threePointersPercentage": "fg3_pct",
        "turnovers": "tov",
        "twoPointersAttempted": "fg2a",
        "twoPointersMade": "fg2m",
        "twoPointersPercentage": "fg2_pct",
        "name": "name",
        "status": "status",
        "personId": "player_id",
        "jerseyNum": "jersey_num",
        "position": "position",
        "starter": "starter",
        "oncourt": "on_court",
        "played": "played",
        "team": "team",
        "Opp": "opp",
        "Game_Clock": "game_clock",
    }
    EXPECTED_COLUMNS = {
        "status": "ACTIVE",
        "order": 1,
        "personId": 1,
        "jerseyNum": 1,
        "position": "PG",
        "starter": 1,
        "oncourt": 1,
        "played": 1,
        "name": "name",
        "nameI": "nameI",
        "firstName": "firstName",
        "familyName": "familyName",
        "notPlayingReason": "notPlayingReason",
        "notPlayingDescription": "notPlayingDescription",
        "assists": 1,
        "blocks": 1,
        "blocksReceived": 1,
        "fieldGoalsAttempted": 1,
        "fieldGoalsMade": 1,
        "fieldGoalsPercentage": 1.0,
        "foulsOffensive": 1,
        "foulsDrawn": 1,
        "foulsPersonal": 1,
        "foulsTechnical": 1,
        "freeThrowsAttempted": 1,
        "freeThrowsMade": 1,
        "freeThrowsPercentage": 1,
        "minus": -1,
        "minutes": "PT01M01.01S",
        "minutesCalculated": "PT01M01.01S",
        "plus": 1,
        "plusMinusPoints": 1,
        "points": 1,
        "pointsFastBreak": 1,
        "pointsInThePaint": 1,
        "pointsSecondChance": 1,
        "reboundsDefensive": 1,
        "reboundsOffensive": 1,
        "reboundsTotal": 1,
        "steals": 1,
        "threePointersAttempted": 1,
        "threePointersMade": 1,
        "threePointersPercentage": 1.0,
        "turnovers": 1,
        "twoPointersAttempted": 1,
        "twoPointersMade": 1,
        "twoPointersPercentage": 1.0,
        "GAME_ID": 1.0,
        "TEAM": "team",
        "OPP": "opp",
    }
    SLEEP_INTERVAL = 0.2


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
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Host": "stats.nba.com",
        "Origin": 'https://www.nba.com',
        "Referer": 'https://www.nba.com/',
        "sec-ch-ua": '"Google Chrome";v="87", ""Not;A\\Brand";v="99", "Chromium";v="87"',
        "sec-ch-ua-mobile": "?1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/87.0.4280.141 Mobile Safari/537.36",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }
    SLEEP_INTERVAL = 2
    GAME_DATE_OBJECT = GameDate()
    START_DATE = GAME_DATE_OBJECT.get_date(2021, 10, 18)
    END_DATE = GAME_DATE_OBJECT.default
    TIMEOUT = 30


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


class TopShotParameters:
    FILE_PATH = "topshot_data.csv"
    HARD_COLUMNS_TO_RETURN = [
        "4h",
        "Circulation Count",
        "Low Ask",
        "Play",
        "Player Name",
        "Series",
        "Set",
        "Tier",
    ]
    FILTER_EASY = None  # {"Series": "1", "Series": "2"}
    FILTER_HARD = None  # {"Top Shot Debut": 1}  # Tier": "Rare", "Tier": "Legendary"
    PLAYER_NAME = "Player Name"
    LOW_ASK = "Low Ask"
    INTEGER_COLUMNS = ["count_easy", "low_ask_easy", "count_hard", "low_ask_hard"]
    NAME_FIXES = {
        "Marcus Morris": "Marcus Morris Sr.",
        "Enes Kanter": "Enes Freedom",
        "Steph Curry": "Stephen Curry",
        "Nicolas Claxton": "Nic Claxton",
    }
    RENAMED_COLUMNS = {
        "Time Stamp (EST)": "date_updated_est",
        "Set_easy": "set_easy",
        "Tier_easy": "tier_easy",
        "Series_easy": "series_easy",
        "Play_easy": "play_easy",
        "Date of Moment": "date_moment",
        "Team": "team",
        "Circulation Count_easy": "count_easy",
        "Owned": "owned",
        "Unique Owners": "unique_owners",
        "In Packs": "in_packs",
        "Minted": "minted",
        "Held by TS": "ts_held",
        "Collector Score": "cs",
        "Low Ask_easy": "low_ask_easy",
        "24h": "24h",
        "7d": "7d",
        "Listings": "listings",
        "Top Shot Debut": "tsd",
        "Rookie Premiere": "rookie_premiere",
        "Rookie Mint": "rookie_mint",
        "Rookie Year": "rookie_year",
        "Edition State": "edition_state",
        "Play ID": "play_id",
        "Set ID": "set_id",
        "Top Shot Link": "ts_link",
        "Set_hard": "set_hard",
        "Tier_hard": "tier_hard",
        "Series_hard": "series_hard",
        "Play_hard": "play_hard",
        "Circulation Count_hard": "count_hard",
        "Low Ask_hard": "low_ask_hard",
    }
    TSD_BACKUP_EASY = True
    TSD_BACKUP_HARD = False
    URL = "https://otmnftapi.com/nbatopshot/create_moments_csv/?user=rydr&"


class WeeklyChallengeParameters:
    CHALLENGE_CATS = ["reb"]
    CHALLENGE_NAME = "### WEEKLY Flash Challenge: 'NO DAYS OFF' "
    CHALLENGE_DESC_EASY = "On Monday, Feb. 7, you'll need any Moment from the NBA player with the most points.  \n " \
                          "On Tuesday, Feb. 8, you'll need any Moment from the NBA player with the most points.  \n " \
                          "On Wednesday, Feb. 9, you'll need any Moment from the NBA player with the most assists.  \n " \
                          "On Thursday, Feb. 10, you'll need any Moment from the NBA player with the most assists.  \n " \
                          "On Friday, Feb. 11, you'll need any Moment from the NBA player with the most rebounds.  \n " \
                          "On **Saturday, Feb. 12**, you'll need any Moment from the NBA player with the most rebounds.  \n " \
                          "On Sunday, Feb. 13, you'll need any Moment from the NBA player with the most three-pointers made."
    CHALLENGE_PREV = pd.DataFrame({
        "date": ["Monday Feb 7", "Tuesday Feb 8", "Wednesday Feb 9", "Thursday Feb 10", "Friday Feb 10"],
        "category": ["pts", "pts", "ast", "ast", "reb"],
        "amount": [38, 44, 11, 19, 19],
        "name": ["Devin Booker", "Giannis Antetokounmpo", "Dennis Smith Jr", "Chris Paul", "Joel Embiid"],
        "team": ["PHX", "MIL", "POR", "PHX", "PHI"]
    }).set_index(['name', 'team'])
    CHALLENGE_ADD_CATEGORIES = None
    CHALLENGE_DESC_HARD = None
    CHALLENGE_SEASON_AVG_OPTIONS = None
    CHALLENGE_SUB_CATEGORIES = None
    CHALLENGE_NUM_HIGHLIGHTED = 1
    TOP_STATS = "top_overall"  # "first_each", "top_each",
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
    TOPSHOT_CATEGORIES = TS_EASY_CATS  # + TS_HARD_CATS


class DailyChallengeParameters:
    CHALLENGE_CATS = ["pts", "reb", "ast", "blk", "stl"]
    CHALLENGE_NAME = "### Weekend Flash Challenge: 'ADD IT UP' "
    CHALLENGE_DESC_EASY = "To earn the Challenge Reward, create a Challenge Entry featuring the top five players " \
                          "with the most combined total Points, Rebounds, Assists, Blocks and Steals in a single" \
                          " game during NBA games from Feb. 11-13, 2022, to earn a Julius Randle Metallic Silver" \
                          " FE Moment™ NFT."
    CHALLENGE_PREV = pd.DataFrame({
        "pts+reb+ast+blk+stl": [61.0, 54.0, 52.0, 52.0, 50.0],
        "on_court": ["GP 02/11"] * 5,
        "differential": [15, 13, 22, -6, 22],
        "plus_minus": [33, 14, 16, 3, 20],
        "name": ["Dejounte Murray", "Joel Embiid", "LaMelo Ball", "Nikola Jokic", "Terry Rozier"],
        "team": ["SAS", "PHI", "CHA", "DEN", "CHA"]}).set_index("name")
    CHALLENGE_ADD_CATEGORIES = CHALLENGE_CATS
    CHALLENGE_DESC_HARD = None
    CHALLENGE_SEASON_AVG_OPTIONS = None
    CHALLENGE_SUB_CATEGORIES = None
    CHALLENGE_NUM_HIGHLIGHTED = 5
    TOP_STATS = "top_overall"  # "first_each", "top_each",
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
    TOPSHOT_CATEGORIES = TS_EASY_CATS  # + TS_HARD_CATS


class WebAppParameters:
    ADDITIONAL_DAY_PATH = "prevgamedays/2022-01-2122_NBAStats_edited.csv"
    AUTO_REFRESH_INTERVAL = 60000  # 1 minute
    AUTO_REFRESH_LIMIT = 120
    CHALLENGE_NOW = False
    CHALLENGE_TYPE = "Daily"
    CSS_PATH = "frontend/css/streamlit.css"
    DEFAULT_CATS = ["min", "on_court"]
    DEFAULT_N_GAMES = 14
    DEFAULT_STAT_CATS = ["pts", "reb", "ast", "stl", "blk", "tov"]
    FILE_NAME_SAVE = "_NBAStats.csv"
    FIRST_TO_THRESHOLD = 5
    IMPORT_ADDITIONAL_DAY = False
    LAST_N_GAMES_OPTIONS = ["All", 30, 14, 7]
    LOGO_PATH = "frontend/nba_logo.png"
    PATH_SAVE = "data/prevgamedays/"
    TIEBREAKERS = ["differential", "plus_minus", "min"]
    TS_EASY_CATS = ["easy_moment", "count_easy", "low_ask_easy", "4hchange_easy"]
    TS_HARD_CATS = ["hard_moment", "count_hard", "low_ask_hard", "4hchange_hard"]
    TOPSHOT_CATEGORIES = TS_EASY_CATS  # + TS_HARD_CATS
