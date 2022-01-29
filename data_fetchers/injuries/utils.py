import requests
from bs4 import BeautifulSoup
import pandas as pd
from data_fetchers.injuries.constants import InjuriesParameters

def get_injury_report(url=InjuriesParameters.URL):
    resp = requests.get(url)
    content = resp.text

    soup = BeautifulSoup(content, "html.parser")

    table = soup.find_all("table")
    list_df = pd.read_html(str(table))
    df = pd.concat(list_df)

    def clean_name(name):
        first_char = name[0]
        last_char = name[-1]
        split_idx = name.find("{}{}".format(last_char, first_char))
        name = name[-(len(name)-split_idx-1):]
        return name

    df["Player"] = df["Player"].apply(clean_name)
    return df

def clean_injury_status(df):
    df["injury_status"] = df["injury_status"].str.replace(
        "Expected to be out until at least","INJ - exp. back"
    )

