DB__SETTINGS_DICT = {
    "defaults": {
        "meta": {
            "schema_version": 1.1,
            "date_initialized": "",
            "date_updated": "",
        },
        "history": {
            "friendlies": {},
        },
        "settings": {
            "friendly": {
                "league_search_depth": "2",
                "match_rules": "cup",
                "opponent_type": "all",
            },
        },
    },
    "history": {
        "meta": {
            "schema_version": 1.6,
            "date_initialized": "",
            "date_updated": "",
        },
        "friendlies": {},
    },
    "settings": {
        "meta": {
            "schema_version": 5.1,
            "date_initialized": "",
            "date_updated": "",
        },
        "friendly": {
            "name": "Friendlies",
            "schema": {
                "league_search_depth": (
                    "League Search Depth",
                    "Default: 2; The higher the number, the deeper the search, the longer it \
                        takes to find potential opponents but also the more potential opponents there are.",
                    ["1", "2", "3"],
                ),
                "match_rules": (
                    "Match Rules",
                    "Default: cup; Rules for the match. See hattrick-handbook for details.",
                    ["normal", "cup"],
                ),
                "opponent_type": (
                    "Opponent Type",
                    "Default: all; Accept either matches against all potential opponents or only against supporters.",
                    ["all", "supporters"],
                ),
            },
        },
    },
}
