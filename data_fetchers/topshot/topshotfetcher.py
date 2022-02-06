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
        self.topshot_data.rename(columns={"4h_easy": "4hchange_easy", "4h_hard": "4hchange_hard"}, inplace=True)
        self.topshot_data["easy_moment"] = (
            self.topshot_data["set_easy"]
            + "-"
            + self.topshot_data["tier_easy"]
            + "-"
            + self.topshot_data["series_easy"]
            + "-"
            + self.topshot_data["play_easy"]
        )
        self.topshot_data["hard_moment"] = (
                self.topshot_data["set_hard"]
                + "-"
                + self.topshot_data["tier_hard"]
                + "-"
                + self.topshot_data["series_hard"]
                + "-"
                + self.topshot_data["play_hard"]
        )
