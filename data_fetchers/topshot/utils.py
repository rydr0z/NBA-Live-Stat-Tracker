import numpy as np
import pandas as pd
import requests

from parameters import TopShotParameters


def get_topshot_data():
    # This function downloads the moment data csv and returns a dataframe
    r = requests.get(TopShotParameters.URL, allow_redirects=True)
    open(TopShotParameters.FILE_PATH, "wb").write(r.content)
    topshot_df = pd.read_csv(TopShotParameters.FILE_PATH)
    return topshot_df


def filter_unreleased(topshot_df):
    # This function filters Low Asks = 0
    # which are new/unreleased moments then omits them
    unreleased_filter = topshot_df[TopShotParameters.LOW_ASK] != 0
    return topshot_df[unreleased_filter]


def get_cheapest_moment(topshot_df, filter_or=None, filter_and=None, tsd_backup=False):
    # This function filters topshot dataframe with only cheapest moment from each player
    topshot_df = filter_unreleased(topshot_df)
    topshot_cheap = topshot_df
    if filter_or is not None:
        topshot_cheap = topshot_cheap[np.logical_or.reduce([topshot_cheap[key] == filter_or[key] for key in filter_or])]
    if filter_and is not None:
        topshot_cheap = topshot_cheap[
            np.logical_and.reduce([topshot_cheap[key] == filter_and[key] for key in filter_and])]
    # get the indices of lowest ask moment for each player and return full filtered dataframe
    if tsd_backup:
        filter_not_tiers = ~topshot_df[TopShotParameters.PLAYER_NAME].isin(
            topshot_cheap[TopShotParameters.PLAYER_NAME].unique()
        )
        filter_tsd = topshot_df["Top Shot Debut"] == 1
        top_shot_debuts = topshot_df[filter_not_tiers][filter_tsd]

        # Combine the two filtered dataframes and get indices of lowest ask moments
        topshot_cheap = pd.concat([topshot_cheap, top_shot_debuts])

    topshot_cheap = (
        topshot_cheap[[TopShotParameters.PLAYER_NAME, TopShotParameters.LOW_ASK]].groupby(
            [TopShotParameters.PLAYER_NAME]).idxmin()
    )
    idx_list = topshot_cheap[TopShotParameters.LOW_ASK].to_list()
    low_ask_df = topshot_df.loc[idx_list]

    return low_ask_df


def fix_topshot_names(topshot_data, name_dict):
    """Fixes certain names using dict where
    key (str) = original name in TS data
    value (str) = new name to match NBA data"""
    for key in name_dict:
        topshot_data.loc[(topshot_data["name"] == key), ["name"]] = name_dict[key]


def combine_topshot_data(raw_data):
    """Fetches all TopShot data, then combines cheapest and hard moments
    then processes the dataframe"""
    topshot_data_cheapest = get_cheapest_moment(raw_data, filter_or=TopShotParameters.FILTER_EASY,
                                                tsd_backup=TopShotParameters.TSD_BACKUP_EASY)

    topshot_data_hard = get_cheapest_moment(raw_data, filter_or=TopShotParameters.FILTER_HARD,
                                            tsd_backup=TopShotParameters.TSD_BACKUP_HARD)

    topshot_data_hard = topshot_data_hard[TopShotParameters.HARD_COLUMNS_TO_RETURN]

    # Rename column used as index then join cheapest and hard moment info
    topshot_data_cheapest.rename(columns={"Player Name": "name"}, inplace=True)
    topshot_data_hard.rename(columns={"Player Name": "name"}, inplace=True)

    topshot_data = topshot_data_cheapest.set_index("name").join(
        topshot_data_hard.set_index("name"),
        on="name",
        lsuffix="_easy",
        rsuffix="_hard",
    )
    topshot_data.reset_index(inplace=True)

    # Removes any accents from names, so that they can be
    # matched with NBA Player Names
    topshot_data.name = (
        topshot_data.name.str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
    )
    topshot_data.name.astype(str)

    # rename all columns for when they are joined to other dataframes
    topshot_data.rename(
        columns=TopShotParameters.RENAMED_COLUMNS,
        inplace=True,
    )

    # Player specific fixes for discrepancies bewteen nba_api name and topshot name
    fix_topshot_names(topshot_data, TopShotParameters.NAME_FIXES)
    topshot_data.set_index("name", inplace=True)

    for col in TopShotParameters.INTEGER_COLUMNS:
        topshot_data[col] = topshot_data[col].fillna(-1)
        topshot_data[col] = topshot_data[col].astype(int)
        topshot_data[col] = topshot_data[col].astype(str)
        topshot_data[col] = topshot_data[col].replace("-1", np.nan)

    return topshot_data


def change_4h_percentage(df):
    col_list = ["4h_easy", "4h_hard"]
    for col in col_list:
        df[col] = df[col] / 100
        df[col] = df[col].map("{:.2%}".format)
