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
            "schema_version": 5.4,
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
                    ["1", "2", "3", "4", "5"],
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


QUOTES = {
    "quotes_ante": [
        "Hey Boss! I'm sure you're quite surprised to see me here. Between you and me: I'm quite new in the flags business. Lovely to share this passion with you! Now to something completely different:",
        "Nice to see you lad! I want to bring this to your attention:",
        "That was a close call! Awful traffic today downtown! Really clever you always take the bus instead. May I bring something up regarding our flags thingy?",
        "Look at you! You look fantastic today my maan! Anyways, you might want to know this:",
    ],
    "quotes_post": [
        "BTW: Did you notice something different about my appearance? That's right! I've shaved my goatee.",
        "What a day! Sorry to interrupt you bro, but I have to rush. It's my turn to pick up the kids today.",
        "It's always a pleasure to have a chat, mate!",
        "Bring your wife and kids next time around!",
    ],
}
