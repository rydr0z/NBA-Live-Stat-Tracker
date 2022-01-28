class TopShotParameters:
    FILE_PATH = "data/topshot_data.csv"
    HARD_COLUMNS_TO_RETURN = [
        "4h",
        "Circulation Count",
        "Low Ask",
        "Play",
        "Player Name",
        "Series",
        "Set",
        "Tier",
    ]
    INTEGER_COLUMNS = ["count_easy", "low_ask_easy", "count_hard", "low_ask_hard"]
    NAME_FIXES = {
        "Marcus Morris": "Marcus Morris Sr.",
        "Enes Kanter": "Enes Freedom",
        "Steph Curry": "Stephen Curry",
    }
    RENAMED_COLUMNS = {
        "Time Stamp (EST)": "date_updated_est",
        "Set_easy": "set_easy",
        "Tier_easy": "tier_easy",
        "Series_easy": "series_easy",
        "Play_easy": "play_easy",
        "Date of Moment": "date_moment",
        "Team": "team",
        "Circulation Count_easy": "count_easy",
        "Owned": "owned",
        "Unique Owners": "unique_owners",
        "In Packs": "in_packs",
        "Minted": "minted",
        "Held by TS": "ts_held",
        "Collector Score": "cs",
        "Low Ask_easy": "low_ask_easy",
        "24h": "24h",
        "7d": "7d",
        "Listings": "listings",
        "Top Shot Debut": "tsd",
        "Rookie Premiere": "rookie_premiere",
        "Rookie Mint": "rookie_mint",
        "Rookie Year": "rookie_year",
        "Edition State": "edition_state",
        "Play ID": "play_id",
        "Set ID": "set_id",
        "Top Shot Link": "ts_link",
        "Set_hard": "set_hard",
        "Tier_hard": "tier_hard",
        "Series_hard": "series_hard",
        "Play_hard": "play_hard",
        "Circulation Count_hard": "count_hard",
        "Low Ask_hard": "low_ask_hard",
    }
    TSD_BACKUP = False
    URL = "https://otmnft.com/create_moments_csv/?playerName=&setName=&team=&minprice=&maxprice=&mincirc=&maxcirc=&sortby="
