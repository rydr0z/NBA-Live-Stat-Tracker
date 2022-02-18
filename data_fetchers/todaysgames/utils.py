from datetime import datetime

import pandas as pd
from nba_api.live.nba.endpoints import scoreboard
from nba_api.stats.endpoints import scoreboardv2

from parameters import TodayParameters


def get_todays_games():
    """Fetch today's game information and store in dataframe"""
    # request today's live scoreboard and get the games
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()
    print(games)

    # initialize dataframe and list to fetched data
    todays_games = pd.DataFrame(columns=TodayParameters.DEFAULT_COLS)

    # loop through today's games, get revelant teams, game clock and scores
    for i, game in enumerate(games):
        away_id = game["awayTeam"]["teamId"]
        home_id = game["homeTeam"]["teamId"]

        game_id = game["gameId"]

        away = game["awayTeam"]["teamTricode"]
        home = game["homeTeam"]["teamTricode"]

        away_score = str(game["awayTeam"]["score"])
        home_score = str(game["homeTeam"]["score"])

        period = str(game["period"])

        # Get Game Clock without additional formatting
        # PT19M00.00S -> 19:00.00
        game_clock = (
            game["gameClock"].replace("PT", "").replace("M", ":").replace("S", "")
        )

        # Convert start time from UTC to EST timezone
        start = datetime.strptime(game["gameTimeUTC"], "%Y-%m-%dT%H:%M:%S%z")
        start = start.astimezone(TodayParameters.TIMEZONE)
        date = start.strftime("%B %d, %Y")

        game_status = game["gameStatusText"]

        # append all values into dataframe
        todays_games = todays_games.append(
            {
                "away_team": away,
                "away_id": away_id,
                "home_team": home,
                "home_id": home_id,
                "period": period,
                "game_clock": game_clock,
                "away_score": away_score,
                "home_score": home_score,
                "start_time": start,
                "game_id": game_id,
                "game_status": game_status,
            },
            ignore_index=True,
        )

    return todays_games.sort_values("start_time"), date


def get_games_on_date(list_of_dates):
    """Fetch today's game information and store in dataframe"""
    # request today's live scoreboard and get the games
    all_games = pd.DataFrame(columns=["GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION"])
    for d in list_of_dates:
        game_date = GameDate()
        date = game_date.get_date(year=d[0], month=d[1], day=d[2])
        board = scoreboardv2.ScoreboardV2(game_date=date)
        games_df = board.line_score.get_data_frame()
        games_df = games_df[["GAME_ID", "TEAM_ID", "TEAM_ABBREVIATION"]]
        all_games = pd.concat([all_games, games_df], axis=0, ignore_index=True)

    return all_games, date
