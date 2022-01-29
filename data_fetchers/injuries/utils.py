import requests
from bs4 import BeautifulSoup
import pandas as pd

resp = requests.get("https://www.cbssports.com/nba/injuries/")
content = resp.text

soup = BeautifulSoup(content, "html.parser")

table = soup.find_all("table")
list_df = pd.read_html(str(table))
df = pd.concat(list_df)


def func(name):
    first_char = name[0]
    last_char = name[-1]
    split_idx = name.find("{}{}".format(last_char, first_char))
    print(split_idx)
    name = name[-(len(name)-split_idx):]
    return name


df["Player"] = df["Player"].apply(func)
print(df.columns)
