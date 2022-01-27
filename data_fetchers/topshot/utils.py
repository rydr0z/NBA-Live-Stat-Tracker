from unicodedata import name
from data_fetchers.topshot.constants import TopShot
import requests
import pandas as pd
import numpy as np


def get_topshot_data():
    # This function downloads the moment data csv and returns a dataframe
    r = requests.get(TopShot.URL, allow_redirects=True)
    open(TopShot.FILE_PATH, "wb").write(r.content)
    topshot_df = pd.read_csv(TopShot.FILE_PATH)
    return topshot_df


def filter_unreleased(topshot_df):
    # This function filters Low Asks = 0
    # which are new/unreleased moments then omits them
    unreleased_filter = topshot_df["Low Ask"] != 0
    return topshot_df[unreleased_filter]


def get_cheapest_moment(topshot_df):
    # This function filters topshot dataframe with only cheapest moment from each player
    topshot_df = filter_unreleased(topshot_df)

    # get the indices of lowest ask moment for each player and return full filtered dataframe
    low_ask_df = (
        topshot_df[["Player Name", "Low Ask"]].groupby(["Player Name"]).idxmin()
    )
    idx_list = low_ask_df["Low Ask"].to_list()
    low_ask_df = topshot_df.loc[idx_list]

    return low_ask_df


def get_hard_moments(topshot_df, tsd_backup=TopShot.TSD_BACKUP):
    """This function filters cheapest moment for each player in any of 
    Fandom, Rare, Legendary Tiers. If there are no moments in any of those tiers,
    it will filter the cheapest Top Shot Debut moment.
    """
    topshot_df = filter_unreleased(topshot_df)

    # Get only moments in desired tiers
    filter_tiers = (
        (topshot_df.Tier == "Rare")
        | (topshot_df.Tier == "Legendary")
        | (topshot_df["Top Shot Debut"] == 1)
    )
    hard_df = topshot_df[filter_tiers]

    # Get TSD moments any players not in tier only if not in the desired tiers
    if tsd_backup:
        filter_not_tiers = ~topshot_df["Player Name"].isin(
            hard_df["Player Name"].unique()
        )
        filter_tsd = topshot_df["Top Shot Debut"] == 1
        top_shot_debuts = topshot_df[filter_not_tiers][filter_tsd]

        # Combine the two filtered dataframes and get indices of lowest ask moments
        hard_df = pd.concat([hard_df, top_shot_debuts])

    hard_df = hard_df[["Player Name", "Low Ask"]].groupby(["Player Name"]).idxmin()
    idx_list = hard_df["Low Ask"].to_list()
    hard_df = topshot_df.loc[idx_list]

    return hard_df[TopShot.HARD_COLUMNS_TO_RETURN]


def fix_topshot_names(topshot_data, name_dict):
    """Fixes certain names using dict where
    key (str) = original name in TS data
    value (str) = new name to match NBA data"""
    for key in name_dict:
        topshot_data.name[topshot_data.name == key] = name_dict[key]


def combine_topshot_data(raw_data):
    """Fetches all TopShot data, then combines cheapest and hard moments
    then processes the dataframe"""
    topshot_data_cheapest = get_cheapest_moment(raw_data)
    topshot_data_hard = get_hard_moments(raw_data)

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
        columns=TopShot.RENAMED_COLUMNS, inplace=True,
    )

    # Player specific fixes for discrepancies bewteen nba_api name and topshot name
    fix_topshot_names(topshot_data, TopShot.NAME_FIXES)
    topshot_data.set_index("name", inplace=True)

    for col in TopShot.INTEGER_COLUMNS:
        topshot_data[col] = topshot_data[col].fillna(-1)
        topshot_data[col] = topshot_data[col].astype(int)
        topshot_data[col] = topshot_data[col].astype(str)
        topshot_data[col] = topshot_data[col].replace("-1", np.nan)

    return topshot_data
