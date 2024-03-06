""" FwF challenge related views """


from datetime import datetime

from flask import (Blueprint, current_app, flash, g, redirect, render_template,
                   request, session, url_for)

from . import api, db, decs, helperf, scheduler

bp_c = Blueprint("challenge", __name__, url_prefix="/challenge")


@bp_c.route("/overview", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_unicorn
@decs.error_check
def overview():
    """ """
    _is_agreed = None
    now = datetime.now()
    g.challenges, *_ = helperf.get_my_challenges()

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
        _xml = api.ht_get_data(
            "worlddetails", countryID="", leagueID=_scheduler_response["country_id"]
        )
        _worlddetails = api.ht_get_worlddetails(_xml)

        g.scheduler_country_id = _scheduler_response["country_id"]
        g.scheduler_run_date = _scheduler_response["date"]
        g.schedule = _scheduler_response
        g.scheduler_country_name = _worlddetails["league_name"]
        g.scheduler_date = datetime.strptime(g.schedule["date"], "%Y%m%d").date()
        g.scheduler_date = g.scheduler_date.strftime("%Y-%m-%d")

        flash("You have a scheduled challenge request.")

    if len(g.challenges) != 0:
        for _challenge in g.challenges:
            is_weekend_match = _challenge[-3]
            tdelta_hours = _challenge[-4]

            if (
                now.weekday() in range(0, 3)
                and tdelta_hours > 100
                and not is_weekend_match
            ) or (
                now.weekday() in range(5, 6) and tdelta_hours > 100 and is_weekend_match
            ):
                message = "Match is running.\
                            Come back Thursday after 7 o'clock UTC to book a new match."

            if _challenge[0]["is_agreed"] == "True":
                _is_agreed = True
                message = "Match booked!"

                _xml = api.ht_get_data(
                    "worlddetails", countryID=_challenge[0]["country_id"], leagueID=""
                )
                _worlddetails = api.ht_get_worlddetails(_xml)

                _xml_data = api.ht_get_data(
                    "matchdetails", matchID=_challenge[0]["match_id"]
                )
                _my_match = api.ht_get_matchdetails(_xml_data)

                if session["teamid"] == _my_match["home_team_id"]:
                    _place = "home"
                else:
                    _place = "away"

                _db_settings = current_app.config["DB__SETTINGS_DICT"]
                _my_document = db.bootstrap_user_document(
                    g.user_id, g.couch, _db_settings
                )
                _my_document = db.set_match_history(
                    g.user_id,
                    g.couch,
                    _worlddetails["league_id"],
                    _challenge[0]["match_id"],
                    _place,
                )
                # Write changements on the history-object to db
                g.couch[g.user_id] = _my_document

        if _is_agreed is None:
            message = "Teams are challenged but not agreed yet."

    else:
        message = "No challenges to show."

    flash(message)

    return render_template("challenge/overview.html")


@bp_c.route("/challenge", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_unicorn
@decs.error_check
def challenge():
    """ """
    if request.method == "POST":
        _challengeable = session["challengeable"]
        _challengeable = list(zip(*_challengeable))[0]
        session.pop("challengeable", None)

        _place = session["place"]
        session.pop("place", None)

        _weekend_friendly = session["weekend_friendly"]
        session.pop("weekend_friendly", None)

        # Set match_rules for match from config and overwrite if custom config is available in db.
        _db_settings = current_app.config["DB__SETTINGS_DICT"]
        _match_rules = _db_settings["defaults"]["settings"]["friendly"]["match_rules"]

        if g.user_id in g.couch:
            _my_document = g.couch[g.user_id]

            if "settings" in _my_document:
                _match_rules = _my_document["settings"]["friendly"]["match_rules"]

        if _place == "home":
            _place = "0"
        else:
            _place = "1"

        if _match_rules == "normal":
            _match_rules = "0"
        else:
            _match_rules = "1"

        try:
            api.ht_do_challenge(
                session["teamid"],
                _challengeable,
                _match_rules,
                _place,
                _weekend_friendly,
            )
            print(f"Would do challenge here { _challengeable }")

        except Exception as e:
            flash(f"Var '{e}' is missing.")

        else:
            flash("Challenges booked!")
            return redirect(url_for("challenge.overview"))

    return render_template("challenge/challenge.html")
