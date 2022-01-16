import streamlit as st
from nba_boxscore_fetcher import *
import time

with open('frontend/css/streamlit.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {display:none}
            </style>
            """
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

df = get_daily_player_data()
df.style.hide_index()

fixed_categories = ['jerseyNum', 'name', 'team','opp','minutes','score','game_clock']
stat_categories = ['points','reboundsTotal','assists','steals','blocks']
sort_by = ['points']
asc_list = [False]

columns = df.columns.sort_values().tolist()

for cat in fixed_categories:
    columns.remove(cat)

options = st.sidebar.multiselect(
     'Which Stat Categories are you interested in?',columns,stat_categories)

categories = fixed_categories+options

st.dataframe(df.sort_values(sort_by, ascending=asc_list)[categories], height=1200)