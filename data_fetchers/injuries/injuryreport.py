from data_fetchers.injuries.utils import get_injury_report


class InjuryReport:
    def __init__(self):
        self.injury_report_df = get_injury_report()
        self.injury_report_df = self.injury_report_df[["Player", "Updated", "Injury Status"]]
        self.injury_report_df.rename(columns={"Player": "name",
                                              "Updated": "injury_updated",
                                              "Injury Status": "injury_status"}, inplace=True)
