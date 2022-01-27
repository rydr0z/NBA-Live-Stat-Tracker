from data_fetchers.topshot.utils import (
    combine_topshot_data,
    get_topshot_data,
    change_4h_percentage,
)
import streamlit as st


class TopShotData:
    def __init__(self):
        self.raw_data = get_topshot_data()
        self.topshot_data = combine_topshot_data(self.raw_data)
        change_4h_percentage(self.topshot_data)
