from data_fetchers.topshot.utils import combine_topshot_data, get_topshot_data


class TopShotData:
    def __init__(self):
        self.raw_data = get_topshot_data()
        self.topshot_data = combine_topshot_data(self.raw_data)
