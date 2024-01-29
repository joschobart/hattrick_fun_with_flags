import functools

from flask import current_app, flash, g, redirect, request, session, url_for

from . import api, db, helperf


def choose_team(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "username" in session:
            helperf.get_my_teams()

            if session["my_team"][session["teamid"]]["team_league_level_unit_id"] == "":
                _xml = api.ht_get_data(
                    "teamdetails", includeFlags="false", teamID=session["teamid"]
                )
                session["my_team"] = api.ht_get_team(_xml)

            _quotes = current_app.config["QUOTES"]
            g.quote_ante, g.quote_post = helperf.random_quotes(_quotes)

            if request.method == "POST" and "teams" in request.form:
                session["teamid"] = request.form["teams"]

                _xml = api.ht_get_data("get_trainer_avatar", teamId=session["teamid"])
                session["trainer_avatar"] = api.ht_get_trainer_avatar(_xml)

                return redirect(url_for("flags.overview"))

        return view(**kwargs)

    return wrapped_view


def error_check(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        error = None

        try:
            return view(**kwargs)

        except Exception as e:
            error = f"Something went wrong on page '{view.__name__}'. \
                    Please try again or report an error to joschobart on hattrick.org. ({e})"

            flash(error)
            return redirect(url_for("index"))

    return wrapped_view


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        username = session.get("username")

        if not username:
            return redirect(url_for("auth.authorize"))

        return view(**kwargs)

    return wrapped_view


def use_db(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if "my_team" in session:
            g.couch = db.get_db()
            g.user_id = session["my_team"]["user"]["user_id"]

        return view(**kwargs)

    return wrapped_view
