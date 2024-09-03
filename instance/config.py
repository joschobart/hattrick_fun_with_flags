COSTS = {
    "costs_per_month": 30,
    "factor_to_euro": 1.0,
}


DB__SETTINGS_DICT = {
    "defaults": {
        "meta": {
            "schema_version": 4.4,
            "date_initialized": "",
            "date_updated": "",
        },
        "history": {
            "friendlies": {},
        },
        "score": {
            "score": {},
            "history": {},
        },
        "settings": {
            "friendly": {
                "league_search_depth": "2",
                "match_rules": "cup",
                "opponent_type": "all",
                "opponent_last_login": "240",
            },
            "locale": {
                "language": "None",
            },
        },
        "unicorn": {
            "stripe": {},
            "unicorn": {},
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
    "score": {
        "meta": {
            "schema_version": 1.5,
            "date_initialized": "",
            "date_updated": "",
        },
        "score": {},
        "history": {},
    },
    "settings": {
        "meta": {
            "schema_version": 6.4,
            "date_initialized": "",
            "date_updated": "",
        },
        "friendly": {
            "en": {
                "name": "Friendlies",
                "schema": {
                    "league_search_depth": (
                        "League Search Depth",
                        "Default: 2; The higher the number, the deeper the search, the longer it \
                            takes to find potential opponents but also the more potential opponents there are.",
                        ["1", "2", "3", "4", "5", "6"],
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
                    "opponent_last_login": (
                        "Opponent Last Login",
                        "Default: 240; Number of hours since the opponent last logged in. You'll wait \
                            longer for results the smaller the number is.",
                        ["0.5", "1", "24", "240"],
                    ),
                },
            },
            "de": {
                "name": "Freundschaftsspiele",
                "schema": {
                    "league_search_depth": (
                        "Durchsuchungstiefe",
                        "Standard: 2; Je höher die Zahl umso tiefer die Suche im Ligabaum. Dadurch \
                            verlängert sich die Suchzeit, aber es vergrössert sich auch die Chance, einen potentiellen Gegner zu finden.",
                        ["1", "2", "3", "4", "5", "6"],
                    ),
                    "match_rules": (
                        "Matchregeln",
                        "Standard: cup; Matchregeln. Siehe Hattrick-Handbuch für Details.",
                        ["normal", "cup"],
                    ),
                    "opponent_type": (
                        "Art der Gegner",
                        "Standard: all; Akzeptiere entweder Spiele gegen alle potentiellen Gegner (all) oder nur gegen Supporter. (supporters)",
                        ["all", "supporters"],
                    ),
                    "opponent_last_login": (
                        "Letzer Login des Gegners",
                        "Standard: 240; Zeitdauer seit dem letzten Login des Gegners in Stunden. Die Suche \
                            wird länger dauern, je kleiner die Zahl ist.",
                        ["0.5", "1", "24", "240"],
                    ),
                },
            },
            "fr": {
                "name": "Matchs amicaux",
                "schema": {
                    "league_search_depth": (
                        "Profondeur de la recherche dans la ligue ",
                        "Par défaut : 2 ; Plus le nombre est élevé, plus la recherche est approfondie, plus il \
                            faut de temps pour trouver des adversaires potentiels, mais aussi plus il y a d'adversaires potentiels.",
                        ["1", "2", "3", "4", "5", "6"],
                    ),
                    "match_rules": (
                        "Règles de match ",
                        "Par défaut : cup ; Règles du match. Voir le manuel hattrick pour plus de détails.",
                        ["normal", "cup"],
                    ),
                    "opponent_type": (
                        "Type d'adversaire ",
                        "Par défaut : all ; Accepter soit des matchs contre tous les adversaires potentiels, soit uniquement contre les HT-supporters.",
                        ["all", "supporters"],
                    ),
                    "opponent_last_login": (
                        "Opponent Last Login",
                        "Default: 240; Number of hours since the opponent last logged in. You'll wait \
                            longer for results the smaller the number is.",
                        ["0.5", "1", "24", "240"],
                    ),
                },
            },
			"tr": {
                "name": "Dostluk maçları",
                "schema": {
                    "league_search_depth": (
                        "Lig arama derinliği ",
                        "Varsayılan: 2; Sayı ne kadar büyük olursa, arama o kadar derin olur, potansiyel rakipleri \
							bulmak o kadar uzun sürer, ancak aynı zamanda potansiyel rakipler de o kadar fazla olur.",
                        ["1", "2", "3", "4", "5", "6"],
                    ),
                    "match_rules": (
                        "Maç kuralları ",
                        "Varsayılan: kupa; Maçın kuralları. Ayrıntılar için hattrick kılavuzuna bakın.",
                        ["normal", "cup"],
                    ),
                    "opponent_type": (
                        "Rakip türü ",
                        "Varsayılan: tümü; Tüm potansiyel rakiplere karşı veya yalnızca HT taraftarlarına karşı yapılacak maçları kabul edin.",
                        ["all", "supporters"],
                    ),
                    "opponent_last_login": (
                        "Rakibin son girişi",
                        "Varsayılan: 240; Rakibin en son oturum açmasından bu yana geçen saat sayısı. Sayı ne kadar \ 
							küçük olursa sonuçlar için o kadar uzun süre beklersiniz..",
                        ["0.5", "1", "24", "240"],
                    ),
                },				
            },         
        },
        "locale": {
            "en": {
                "name": "Locale",
                "schema": {
                    "language": (
                        "Language",
                        "Default: en; Choose your language. This has priority over your browser settings.",
                        ["en", "de", "fr", "tr"],
                    ),
                },
            },
            "de": {
                "name": "Sprache",
                "schema": {
                    "language": (
                        "Sprache",
                        "Standard: en; Wähle deine Sprache. Dies hat Vorrang vor deinen Browsereinstellungen.",
                        ["en", "de", "fr", "tr"],
                    ),
                },
            },
            "fr": {
                "name": "Langue",
                "schema": {
                    "language": (
                        "Langue ",
                        "Par défaut : en ; Choisissez votre langue. Ce choix a la priorité sur les paramètres de votre navigateur.",
                        ["en", "de", "fr", "tr"],
                    ),
                },
            },
            "tr": {
                "name": "Dil",
                "schema": {
                    "language": (
                        "Dil ",
                        "Varsayılan: en ; Dilinizi seçin. Bu seçim tarayıcı ayarlarınıza göre önceliklidir.",
                        ["en", "de", "fr", "tr"],
                    ),
                },
            },
        },
    },
    "unicorn": {
        "meta": {
            "schema_version": 1.0,
            "date_initialized": "",
            "date_updated": "",
        },
        "stripe": {
            "username": "",
            "sessions": {},
        },
        "unicorn": "",
    },
}


QUOTES = {
    "quotes_ante": {
        "en": [
            "Hey Boss! I'm sure you're quite surprised to see me here. Between you and me: I'm quite new in the flags business. Lovely to share this passion with you! Now to something completely different:",
            "Nice to see you lad! I want to bring this to your attention:",
            "That was a close call! Awful traffic today downtown! Really clever you always take the bus instead. May I bring something up regarding our flags thingy?",
            "Look at you! You look fantastic today my maan! Anyways, you might want to know this:",
        ],
        "de": [
            "Hey Boss! Ich bin mir sicher, dass du ziemlich überrascht bist, mich hier zu sehen. Zwischen uns: Ich bin ziemlich neu im Flaggen-Geschäft. Schön, diese Leidenschaft mit dir zu teilen! Jetzt zu etwas völlig anderem:",
            "Schön dich zu sehen, Kumpel! Ich möchte dir das hier ans Herz legen:",
            "Das war knapp! Schrecklicher Verkehr heute in der Innenstadt! Wirklich klug, dass du immer den Bus nimmst. Darf ich etwas im Zusammenhang mit unserem Flaggen-Ding ansprechen?",
            "Schau dich an! Du siehst fantastisch aus heute, mein Freund! Wie auch immer, du möchtest vielleicht folgendes wissen:",
        ],
        "fr": [
            "Hey Boss ! Je suis sûr que tu es plutôt surpris de me voir ici. Entre nous, je suis assez novice dans le domaine des drapeaux. Mais c'est un plaisir de partager cette passion avec toi ! À présent, changeons de sujet :",
            "Content de te voir partenaire ! Je souhaite attirer ton attention sur ce point :",
            "C'était moins une ! La circulation en ville est infernale aujourd'hui ! C'est bien vu de ta part de toujours prendre les transports en commun. Je peux te parler de notre petite affaire de drapeaux ?",
            "Regardez-moi ça ! T'as l'air fantastique aujourd'hui, l'artiste ! Quoi qu'il en soit, il est bon que tu saches ceci :",
        ],
		"tr": [
            "Hey patron! Eminim beni burada gördüğüne çok şaşırmışsındır. Aramızda kalsın, bayraklar konusunda oldukça yeniyim. Ama bu tutkuyu sizinle paylaşmak bir zevk! Şimdi konuyu değiştirelim:",
            "Seni gördüğüme sevindim dostum! Size şunu tavsiye etmek isterim:",
            "Yetiştim! Bugün şehir merkezinde trafik berbat! Her zaman otobüse binmen gerçekten akıllıca. Bayraklarımızla ilgili bir şeyden bahsedebilir miyim?",
            "Şuna bir bak! Bugün harika görünüyorsun dostum! Her neyse, aşağıdakileri bilmek isteyebilirsiniz:",
        ],        
    },
    "quotes_post": {
        "en": [
            "BTW: Did you notice something different about my appearance? That's right! I've shaved my goatee.",
            "What a day! Sorry to interrupt you bro, but I have to rush. It's my turn to pick up the kids today.",
            "It's always a pleasure to have a chat, mate!",
            "Bring your wife and kids next time around!",
        ],
        "de": [
            "Übrigens: Hast du etwas an meinem Aussehen bemerkt? Richtig! Ich habe meinen Ziegenbart rasiert.",
            "Was für ein Tag! Entschuldigung, dass ich dich unterbreche, aber ich muss mich beeilen. Heute bin ich dran, die Kinder abzuholen.",
            "Es ist immer ein Vergnügen, ein Schwätzchen zu halten, mein Freund!",
            "Bring deine Frau und Kinder das nächste Mal!",
        ],
        "fr": [
            "Au fait, t'as pas remarqué un truc différent concernant mon apparence ? Exact ! J'ai rasé ma barbichette.",
            "Quelle journée ! Désolé ma gueule, mais je dois me dépêcher. C'est mon tour d'aller chercher les mômes aujourd'hui.",
            "C'est toujours un plaisir de discuter avec toi, camarade !",
            "Amène ta femme et tes gosses la prochaine fois !",
        ],
		"tr": [
            "Bu arada: Görünüşümle ilgili bir şey fark ettin mi? Doğru! Keçi sakalımı tıraş ettim.",
            "Ne gün! Kardeşim, böldüğüm için özür dilerim ama acele etmem gerekiyor. Bugün çocukları alma sırası bende.",
            "Sohbet etmek her zaman bir zevktir dostum!",
            "Bir dahaki sefere eşinizi ve çocuklarınızı getirin!",
        ],        
    },
}
