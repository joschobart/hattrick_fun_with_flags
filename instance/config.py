DB__SETTINGS_DICT = {
    "meta": {
        "schema_version": 3,
        "date_initialized": "",
        "date_updated": "",
    },
    "objects": {
        "friendly": {
            "name": "Friendlies",
            "schema": {
                "league_search_depth": (
                    "League Search Depth",
                    ["0", "1", "2", "3", "4"],  # default: 2, the higher the slower
                ),
                "match_rules": ("Match Rules", ["normal", "cup"]),  # default: cup
                "opponent_type": (
                    "Opponent Type",
                    ["all", "supporters"],  # default: all
                ),
            },
        },
    },
    "defaults": {
        "friendly": {
            "league_search_depth": "2",
            "match_rules": "cup",
            "opponent_type": "all",
        },
    },
}
