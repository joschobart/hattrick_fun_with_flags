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
    teamid = session.get("teamid", None)

    if g.challenges["challenges"] != []:
        if g.challenges["challenges"][0]["is_agreed"] == "True":
            if now.weekday() in range(0, 3) and g.tdelta_hours > 100:
                message = f"Match is running.\
                            Come back Thursday after 7 o'clock UTC to book a new match."

                session["my_team"][session["teamid"]]["has_friendly"] = None
                g.challenges.clear()

            else:
                message = f"Match booked!"

                session["my_team"][session["teamid"]]["has_friendly"] = match_time

        else:
            message = f"Teams are challenged but not agreed yet."

    else:
        message = f"No challenges to show"

        session["my_team"][session["teamid"]]["has_friendly"] = None

    flash(message)

    return render_template("challenge/overview.html")


@bp_c.route("/challenge", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
# @decs.error_check
def challenge():
    if request.method == "POST":
        # Set match_rules for match from config and overwrite if custom config is available in db.
        _db_settings = current_app.config["DB__SETTINGS_DICT"]
        _match_rules = _db_settings["defaults"]["match_rules"]

        if g.user_id in g.couch:
            _my_document = g.couch[g.user_id]

            if "settings" in _my_document:
                _match_rules = _my_document["friendly"]["match_rules"]
        print(_match_rules)

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
            # challenge = api.ht_do_challenge(session['teamid'], g.challengeable, match_type, g.place)
            print(f"match_type: {_match_rules}, match_place: {_place}")

        except Exception as e:
            flash(f"Var '{e}' is missing.")

        else:
            flash("Challenges booked!")
            return redirect(url_for("challenge.overview"))

    return render_template("challenge/challenge.html")
