import pandas as pd
from datetime import datetime
from data_fetchers.todaysgames.constants import TodayParameters
from nba_api.live.nba.endpoints import scoreboard


def get_todays_games():
    """Fetch today's game information and store in dataframe"""
    # request today's live scoreboard and get the games
    board = scoreboard.ScoreBoard()
    games = board.games.get_dict()

    # initialize dataframe and list to fetched data
    todays_games = pd.DataFrame(columns=TodayParameters.DEFAULT_COLS)

    # loop through today's games, get revelant teams, game clock and scores
    for i, game in enumerate(games):
        awayId = game["awayTeam"]["teamId"]
        homeId = game["homeTeam"]["teamId"]

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
                "away_id": awayId,
                "home_team": home,
                "home_id": homeId,
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
