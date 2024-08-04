"""FwF app related core views"""

from flask import (Blueprint, current_app, flash, g, render_template, request,
                   session)
from flask_babel import gettext

from . import api, db, decs, helperf, scheduler

bp_f = Blueprint("flags", __name__, url_prefix="/flags")


@bp_f.route("/overview", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.set_config_from_db
@decs.error_check
def overview():
    """ """
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
@decs.set_config_from_db
@decs.error_check
def details():
    """ """
    _settings = current_app.config["DB__SETTINGS_DICT"]

    if "challengeable" in session:
        session.pop("challengeable", None)

    challengeable = []

    g.bookable = True

    g.flagid = request.args.get("flagid")

    g.place = request.args.get("place")

    g.l_home, g.l_away, *_ = helperf.compose_flag_matrix(session["teamid"])

    gmc, bookable_slot = helperf.get_my_challenges()

    if gmc:
        g.weekend_bookable = True
        for challenge in gmc:
            if not challenge[-1]:
                g.weekend_bookable = False

            if not challenge[-2]:
                g.bookable = False

    if not bookable_slot:
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

    _scheduler_object = {
        "type": "get_schedule",
        "data": {
            "object": {
                "team_id": session["teamid"],
            },
        },
    }
    _scheduler_response = scheduler.schedule(_scheduler_object)
    if isinstance(_scheduler_response, dict):
        g.schedule = _scheduler_response
        _xml = api.ht_get_data(
            "worlddetails", countryID="", leagueID=g.schedule["country_id"]
        )
        _worlddetails = api.ht_get_worlddetails(_xml)
        g.scheduler_country_name = _worlddetails["league_name"]

    (
        _opponent_type,
        _match_rules,
        _league_search_depth,
        _opponent_last_login,
    ) = db.get_settings(g.user_id, g.couch, _settings)
    g.played_matches = db.get_match_history(g.user_id, g.couch, g.flagid, g.place)

    if request.method == "POST":
        if "user_added_friendly" in request.form:
            _user_added_friendly = request.form["user_added_friendly"]

            _xml_data = api.ht_get_data(
                "matchdetails", teamID=session["teamid"], matchID=_user_added_friendly
            )
            try:
                _my_match = api.ht_get_matchdetails(_xml_data)

            except AttributeError:
                flash(gettext("Match not found."))

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
                            flash(
                                gettext("{_place}-match added.".format(_place=_place))
                            )
                            g.my_document = db.bootstrap_user_document(
                                g.user_id, g.couch, _settings
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
                                gettext(
                                    "Not one of your past friendly-matches for that flag."
                                )
                            )
                        break

                    else:
                        continue

                flash("Not one of your past friendly-matches.")

        elif "match_type" in request.form:
            weekend_friendly = request.form["match_type"]

            sl = helperf.get_series_list(
                g.flagid, search_level=int(_league_search_depth)
            )

            challengeable = helperf.get_challengeable_teams_list(
                session["teamid"],
                g.place,
                sl,
                weekend_friendly,
                _opponent_type,
                _opponent_last_login,
            )
            session["weekend_friendly"] = weekend_friendly
            session["place"] = g.place
            session["challengeable"] = challengeable

        elif "schedule_friendly" in request.form:
            _object = {
                "type": "add_schedule",
                "data": {
                    "object": {
                        "team_id": session["teamid"],
                        "fernet_token": session["encrypted_access_token"],
                        "country_id": g.flagid,
                        "match_place": g.place,
                        "match_rules": _match_rules,
                        "opponent_type": _opponent_type,
                        "search_depth": _league_search_depth,
                        "weekend_friendly": "0",
                    },
                },
            }

            scheduler.schedule(_object)
            flash(
                gettext(
                    "Schedule for challenge is booked. You find it under 'Challenges'."
                )
            )

        elif "delete_schedule" in request.form:
            _object = {
                "type": "delete_schedule",
                "data": {
                    "object": {
                        "team_id": session["teamid"],
                        "fernet_token": session["encrypted_access_token"],
                    },
                },
            }

            scheduler.schedule(_object)
            flash(gettext("Schedule for challenge is deleted successfully."))

    return render_template("flags/details.html")
