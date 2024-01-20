from datetime import datetime

from flask import (
    Blueprint,
    current_app,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from . import api, db, decs, helperf

bp_c = Blueprint("challenge", __name__, url_prefix="/challenge")


@bp_c.route("/overview", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
# @decs.error_check
def overview():
    (
        g.challenges,
        now,
        match_time,
        tdelta,
        g.tdelta_hours,
        bookable,
    ) = helperf.get_my_challenges()

    if g.challenges["challenges"] != []:
        if g.challenges["challenges"][0]["is_agreed"] == "True":
            _xml_data = api.ht_get_data(
                "matchdetails",
                teamID=session["teamid"],
                matchID=g.challenges["challenges"][0]["match_id"],
            )
            _my_match = api.ht_get_matchdetails(_xml_data)
            if _my_match["home_team_id"] == session["teamid"]:
                session["place"] = "home"
            else:
                session["place"] = "away"

            g.db_settings = current_app.config["DB__SETTINGS_DICT"]
            g.my_document = db.bootstrap_document(g.user_id, g.couch, g.db_settings)

            if session["teamid"] not in g.my_document["history"]["friendlies"]:
                g.my_document["history"]["friendlies"][session["teamid"]] = {
                    "opponent_country": {}
                }

            if (
                g.challenges["challenges"][0]["country_id"]
                not in g.my_document["history"]["friendlies"][session["teamid"]][
                    "opponent_country"
                ]
            ):
                g.my_document["history"]["friendlies"][session["teamid"]][
                    "opponent_country"
                ][g.challenges["challenges"][0]["country_id"]] = {
                    "home": [],
                    "away": [],
                }

            if (
                g.challenges["challenges"][0]["match_id"]
                not in g.my_document["history"]["friendlies"][session["teamid"]][
                    "opponent_country"
                ][g.challenges["challenges"][0]["country_id"]][session["place"]]
            ):
                g.my_document["history"]["friendlies"][session["teamid"]][
                    "opponent_country"
                ][g.challenges["challenges"][0]["country_id"]][session["place"]].append(
                    g.challenges["challenges"][0]["match_id"]
                )

                g.my_document["history"]["meta"]["date_updated"] = str(
                    datetime.utcnow()
                )

            # Write changements on the history-object to db
            g.couch[g.user_id] = g.my_document

            if now.weekday() in range(0, 3) and g.tdelta_hours > 100:
                message = "Match is running.\
                            Come back Thursday after 7 o'clock UTC to book a new match."

                session["my_team"][session["teamid"]]["has_friendly"] = None
                g.challenges.clear()

            else:
                message = "Match booked!"

                session["my_team"][session["teamid"]]["has_friendly"] = match_time

        else:
            message = "Teams are challenged but not agreed yet."

    else:
        message = "No challenges to show."

        session["my_team"][session["teamid"]]["has_friendly"] = None

    flash(message)

    return render_template("challenge/overview.html")


@bp_c.route("/challenge", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.error_check
def challenge():
    if request.method == "POST":
        # Set match_rules for match from config and overwrite if custom config is available in db.
        _db_settings = current_app.config["DB__SETTINGS_DICT"]
        _match_rules = _db_settings["defaults"]["settings"]["friendly"]["match_rules"]

        if g.user_id in g.couch:
            _my_document = g.couch[g.user_id]

            if "settings" in _my_document:
                _match_rules = _my_document["settings"]["friendly"]["match_rules"]

        g.challengeable = list(zip(*session.get("challengeable", None)))[0]
        _place = session.get("place", None)

        session.pop("challengeable", None)
        session.pop("place", None)

        if _place == "home":
            _place = "0"
        else:
            _place = "1"

        if _match_rules == "normal":
            _match_rules = "0"
        else:
            _match_rules = "1"

        try:
            # api.ht_do_challenge(
            #     session["teamid"], g.challengeable, _match_rules, _place
            # )
            print("Would do challenge here")

        except Exception as e:
            flash(f"Var '{e}' is missing.")

        else:
            flash("Challenges booked!")
            return redirect(url_for("challenge.overview"))

    return render_template("challenge/challenge.html")
