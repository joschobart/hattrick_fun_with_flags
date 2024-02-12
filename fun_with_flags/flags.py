from datetime import datetime

from flask import Blueprint, current_app, flash, g, render_template, request, session

from . import api, db, decs, helperf

bp_f = Blueprint("flags", __name__, url_prefix="/flags")


@bp_f.route("/overview", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.set_unicorn
@decs.error_check
def overview():
    (
        g.l_home,
        g.l_away,
        g.nr_flags_home,
        g.nr_flags_away,
        *_,
    ) = helperf.compose_flag_matrix(session["teamid"])

    g.l_home = sorted(g.l_home, key=lambda x: x[1].lower())
    g.l_away = sorted(g.l_away, key=lambda x: x[1].lower())

    return render_template("flags/overview.html", svg_image=_[0])


@bp_f.route("/details", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_unicorn
# @decs.error_check
def details():
    challengeable = []

    g.flagid = request.args.get("flagid")

    g.place = request.args.get("place")

    g.l_home, g.l_away, *_ = helperf.compose_flag_matrix(session["teamid"])

    gmc = helperf.get_my_challenges()

    if gmc:
        g.weekend_bookable = True
        g.bookable = True
        for challenge in gmc:
            if not challenge[-1]:
                g.weekend_bookable = False

            if not challenge[-2]:
                g.bookable = False

    for item in session["teams"]:
        if int(item[0]) == int(session["teamid"]):
            g.team = item[1]
            break

    if g.place == "home":
        func = g.l_home[:]
    else:
        func = g.l_away[:]

    for item in func:
        if int(item[0]) == int(g.flagid):
            g.nation = item[1]
            g.flagurl = item[2]

            if "inactive" in g.flagurl:
                g.missing_flag = True
            else:
                g.missing_flag = False
            break

    if g.user_id in g.couch:
        _my_document = g.couch[g.user_id]

        if g.missing_flag:
            # Set opponent_type for match and league_search_depth
            # from config and overwrite if custom config is available in db.
            _db_settings = current_app.config["DB__SETTINGS_DICT"]
            _opponent_type = _db_settings["defaults"]["settings"]["friendly"][
                "opponent_type"
            ]
            _league_search_depth = _db_settings["defaults"]["settings"]["friendly"][
                "league_search_depth"
            ]

            if "settings" in _my_document:
                _opponent_type = _my_document["settings"]["friendly"]["opponent_type"]
                _league_search_depth = _my_document["settings"]["friendly"][
                    "league_search_depth"
                ]

        if "history" in _my_document:
            g.played_matches = []

            if session["teamid"] in _my_document["history"]["friendlies"]:
                if (
                    g.flagid
                    in _my_document["history"]["friendlies"][session["teamid"]][
                        "opponent_country"
                    ]
                ):
                    for _match in _my_document["history"]["friendlies"][
                        session["teamid"]
                    ]["opponent_country"][g.flagid][g.place]:
                        _xml_data = api.ht_get_data(
                            "matchdetails", teamID=session["teamid"], matchID=_match
                        )
                        _my_match = api.ht_get_matchdetails(_xml_data)
                        _match_date = datetime.strptime(
                            _my_match["match_date"], "%Y-%m-%d %H:%M:%S"
                        )
                        _timedelta = datetime.now() - _match_date
                        _timedelta = _timedelta.total_seconds()

                        if _timedelta > 0:
                            _match_date = _match_date.strftime("%d.%m.%Y %H:%M")
                            _my_match["match_date"] = _match_date
                            g.played_matches.append(_my_match)

    if request.method == "POST":
        if request.form["user_added_friendly"]:
            _user_added_friendly = request.form["user_added_friendly"]

            _xml_data = api.ht_get_data(
                "matchdetails", teamID=session["teamid"], matchID=_user_added_friendly
            )
            try:
                _my_match = api.ht_get_matchdetails(_xml_data)

            except AttributeError:
                flash("Match not found.")

            else:
                for home_away in ["home_team_id", "away_team_id"]:
                    if _my_match[home_away] == session["teamid"]:
                        if _my_match["home_team_id"] == session["teamid"]:
                            _opponent_teamid = _my_match["away_team_id"]
                            _place = "home"
                        else:
                            _opponent_teamid = _my_match["home_team_id"]
                            _place = "away"

                        _xml = api.ht_get_data(
                            "teamdetails", teamID=_opponent_teamid, includeFlags="false"
                        )
                        _opponent = api.ht_get_team(_xml)
                        _match_country = _opponent[_opponent_teamid]["team_country_id"]

                        if _match_country == g.flagid:
                            flash(f"{_place}-match added.")
                            g.db_settings = current_app.config["DB__SETTINGS_DICT"]
                            g.my_document = db.bootstrap_user_document(
                                g.user_id, g.couch, g.db_settings
                            )
                            g.my_document = db.set_match_history(
                                g.user_id,
                                g.couch,
                                _match_country,
                                _user_added_friendly,
                                _place,
                            )
                            # Write changements on the history-object to db
                            g.couch[g.user_id] = g.my_document

                        else:
                            flash(
                                "Not one of your past friendly-matches for that flag."
                            )
                        break

                    else:
                        continue

                flash("Not one of your past friendly-matches.")

        elif request.form["match_type"]:
            weekend_friendly = request.form["match_type"]

            sl = helperf.get_series_list(
                g.flagid, search_level=int(_league_search_depth)
            )

            challengeable = helperf.get_challengeable_teams_list(
                session["teamid"], g.place, sl, weekend_friendly, _opponent_type
            )

            session["weekend_friendly"] = weekend_friendly
            session["place"] = g.place
            session["challengeable"] = challengeable

    return render_template("flags/details.html")
