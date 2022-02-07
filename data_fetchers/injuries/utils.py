import pandas as pd
import requests
from bs4 import BeautifulSoup

from parameters import InjuriesParameters


def clean_name(name):
    """Cleans the player name formatted as 'F. LastFirst Last' and return First Last"""
    first_char = name[0]
    last_char = name[-1]
    split_idx = name.find("{}{}".format(last_char, first_char))
    name = name[-(len(name) - split_idx - 1):]
    return name


def clean_injury_status(df):
    """Change injury status notes so that it is more succint"""
    for key in InjuriesParameters.REPLACE_STR:
        df["Injury Status"] = df["Injury Status"].str.replace(key, InjuriesParameters.REPLACE_STR[key])


def get_injury_report(url=InjuriesParameters.URL):
    """Given the url to the webpage with injuries, scrape all tables and return as a dataframe"""
    resp = requests.get(url)
    content = resp.text

    soup = BeautifulSoup(content, "html.parser")

    table = soup.find_all("table")
    list_df = pd.read_html(str(table))

    df = pd.concat(list_df)

    # Clean dataframe before returning
    df["Player"] = df["Player"].apply(clean_name)
    clean_injury_status(df)

    return df
