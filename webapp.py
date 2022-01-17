import requests
import pandas as pd
from datetime import datetime
import pytz
import streamlit as st
import numpy as np
import time

from nba_boxscore_fetcher import Stat_Dataset

def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

with open('frontend/css/streamlit.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

pd.options.display.float_format = '{:,.0f}'.format

today_dataset = Stat_Dataset(topshot_data_url="https://otmnft.com/create_moments_csv/?playerName=&setName=&team=&minprice=&maxprice=&mincirc=&maxcirc=&sortby=")
df = today_dataset.gameday_df

df.style.hide_index()

df['EASY MOMENT'] = df['SET_EASY']+'-'+df['TIER_EASY']+'-'+df['SERIES_EASY']+'-'+df['PLAY_EASY']
df['HARD MOMENT'] = df['SET_HARD']+'-'+df['TIER_HARD']+'-'+df['SERIES_HARD']+'-'+df['PLAY_HARD']
fixed_categories = ['TEAM_NBA','OPPONENT','SCORE','GAME CLOCK','MINUTES'] 
EASY_categories = ['EASY MOMENT','COUNT_EASY','LOW ASK_EASY']
HARD_categories = ['HARD MOMENT','COUNT_HARD','LOW ASK_HARD']
topshot_categories = EASY_categories + HARD_categories

columns = today_dataset.stat_categories_integer + today_dataset.stat_categories_percentages
columns = [ x.upper() for x in columns ]
columns.sort()

stat_categories = ['POINTS','REBOUNDSTOTAL','ASSISTS','STEALS','BLOCKS']
options = st.sidebar.multiselect(
     'Which stats are you interested in?',columns,stat_categories)

add_categories = st.sidebar.multiselect(
     'Do you want to add up any categories?',columns)
add_categories_combined = "+".join(add_categories)

sub_categories = st.sidebar.multiselect(
    'Do you want to subtract any categories? Categories are subtracted from the first listed',columns
)
sub_categories_combined = "-".join(sub_categories)

challenge = st.sidebar.checkbox("Check here to use challenge settings")
challenge_cats = ['MINUTES']

st.sidebar.button("Click Here to Refresh Live Data")
if add_categories:
    df[add_categories_combined] = 0

    for cat in add_categories:
        df[add_categories_combined] += df[cat]

if sub_categories:
    df[sub_categories_combined] = df[sub_categories[0]]

    for cat in sub_categories:
        if cat != sub_categories[0]:
            df[sub_categories_combined] -= df[cat]

if add_categories and sub_categories:
    categories = fixed_categories+[add_categories_combined, sub_categories_combined]+options+topshot_categories
    sort_by = [add_categories_combined, sub_categories_combined, 'MINUTES']
    asc_list = [False, False, False]
elif add_categories:
    categories = fixed_categories+[add_categories_combined]+options+topshot_categories
    sort_by = [add_categories_combined, 'MINUTES']
    asc_list = [False, False]
elif sub_categories:
    categories = fixed_categories+[sub_categories_combined]+options+topshot_categories
    sort_by = [sub_categories_combined, 'MINUTES']
    asc_list = [False, False]
else:
    categories = fixed_categories+options+topshot_categories
    sort_by = ['POINTS', 'MINUTES']
    asc_list = [False, False]
active_only = df['STATUS']=="ACTIVE"

if challenge:
    categories = fixed_categories+topshot_categories
    options=[]
    sort_by = challenge_cats
    asc_list = [False]

todays_games = pd.DataFrame(today_dataset.todays_games, index=today_dataset.start_times, columns=['Game'])
st.write("NBA Stat Tracker for {}".format(today_dataset.game_date))
st.table(todays_games.sort_values(by=['Game']).sort_index())
st.dataframe(df[active_only].sort_values(sort_by, ascending=asc_list)[categories], height=1200)
