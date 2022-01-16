import streamlit as st
from nba_boxscore_fetcher import *
import time

with open('frontend/css/streamlit.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

df = get_daily_player_data()
df.style.hide_index()

df['moment'] = df['Set']+'-'+df['Tier']+'-'+df['Series']+'-'+df['Play']
fixed_categories = ['jerseyNum']
game_detail_categories = ['team','opp', 'minutes','score','game_clock']
topshot_categories = ['moment','Circulation Count','Low Ask']
stat_categories = ['points','reboundsTotal','assists','steals','blocks']
sort_by = ['points', 'minutes']
asc_list = [False, False]

columns = df.columns.sort_values().tolist()

for cat in fixed_categories:
    columns.remove(cat)

options = st.sidebar.multiselect(
     'Which Stat Categories are you interested in?',columns,stat_categories)

categories = fixed_categories+options+game_detail_categories+stat_categories

st.dataframe(df.sort_values(sort_by, ascending=asc_list)[categories], height=1200)