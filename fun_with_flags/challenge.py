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
    def get_challenges_list(is_weekend_match=False):
        (
            challenges,
            now,
            match_time,
            tdelta,
            tdelta_hours,
            bookable,
        ) = helperf.get_my_challenges(
            flagid=session["my_team"][str(session["teamid"])]["team_country_id"],
            is_weekend_match=is_weekend_match,
        )

        if challenges["challenges"] != []:
            if challenges["challenges"][0]["is_agreed"] == "True":
                _xml = api.ht_get_data(
                    "worlddetails", countryID=challenges["challenges"][0]["country_id"]
                )
                _worlddetails = api.ht_get_worlddetails(_xml)

                _xml_data = api.ht_get_data(
                    "matchdetails",
                    teamID=session["teamid"],
                    matchID=challenges["challenges"][0]["match_id"],
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
                    _worlddetails["league_id"]
                    not in g.my_document["history"]["friendlies"][session["teamid"]][
                        "opponent_country"
                    ]
                ):
                    g.my_document["history"]["friendlies"][session["teamid"]][
                        "opponent_country"
                    ][_worlddetails["league_id"]] = {
                        "home": [],
                        "away": [],
                    }

                if (
                    challenges["challenges"][0]["match_id"]
                    not in g.my_document["history"]["friendlies"][session["teamid"]][
                        "opponent_country"
                    ][_worlddetails["league_id"]][session["place"]]
                ):
                    g.my_document["history"]["friendlies"][session["teamid"]][
                        "opponent_country"
                    ][_worlddetails["league_id"]][session["place"]].append(
                        challenges["challenges"][0]["match_id"]
                    )

                    g.my_document["history"]["meta"]["date_updated"] = str(
                        datetime.utcnow()
                    )

                # Write changements on the history-object to db
                g.couch[g.user_id] = g.my_document

                if (
                    now.weekday() in range(0, 3)
                    and tdelta_hours > 100
                    and not is_weekend_match
                ):
                    message = "Match is running.\
                                Come back Thursday after 7 o'clock UTC to book a new match."

                    session["my_team"][session["teamid"]]["has_friendly"] = None
                    challenges.clear()
                elif is_weekend_match:
                    if now.weekday() == 5 and tdelta_hours > 100:
                        message = "Weekend-Match is running."
                    else:
                        message = "Match booked!"

                else:
                    message = "Match booked!"

                    session["my_team"][session["teamid"]]["has_friendly"] = match_time

            else:
                message = "Teams are challenged but not agreed yet."

        else:
            message = "No challenges to show."

            session["my_team"][session["teamid"]]["has_friendly"] = None

        flash(message)

        return challenges, tdelta_hours

    g.challenges, g.tdelta_hours = get_challenges_list()

    _xml = api.ht_get_data(
        "worlddetails",
        leagueID=session["my_team"][str(session["teamid"])]["team_country_id"],
    )
    _worlddetails = api.ht_get_worlddetails(_xml)

    if int(_worlddetails["season_round"]) > 14:
        weekend_friendly, g.tdelta_hours_weekend = get_challenges_list(
            is_weekend_match=True
        )

        if g.tdelta_hours_weekend != 0:
            g.is_weekend_match = True

            weekend_friendly = weekend_friendly["challenges"][0]
            g.challenges["challenges"].append(weekend_friendly)

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
