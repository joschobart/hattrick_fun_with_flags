from datetime import datetime

from flask import Blueprint, current_app, g, render_template, request, session

from . import api, decs, helperf

bp_f = Blueprint("flags", __name__, url_prefix="/flags")


@bp_f.route("/overview", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
#@decs.error_check
def overview():
    g.l_home, g.l_away, g.nr_flags_home, g.nr_flags_away, *_ = helperf.compose_flag_matrix(
        session["teamid"]
    )

    g.l_home = sorted(g.l_home, key=lambda x: x[1].lower())
    g.l_away = sorted(g.l_away, key=lambda x: x[1].lower())

    return render_template("flags/overview.html", svg_image=_[0])


@bp_f.route("/details", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.error_check
def details():
    g.challengeable = []

    g.flagid = request.args.get("flagid")

    session["place"] = request.args.get("place")

    g.l_home, g.l_away, *_ = helperf.compose_flag_matrix(session["teamid"])

    gmc = helperf.get_my_challenges()
    g.bookable = gmc[-1]

    for item in session["teams"]:
        if int(item[0]) == int(session["teamid"]):
            g.team = item[1]
            break

    if session["place"] == "home":
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

    if request.method == "POST":
        if g.missing_flag:
            # Set opponent_type for match and league_search_depth
            # from config and overwrite if custom config is available in db.
            _db_settings = current_app.config["DB__SETTINGS_DICT"]
            _opponent_type = _db_settings["defaults"]["friendly"]["opponent_type"]
            _league_search_depth = _db_settings["defaults"]["friendly"][
                "league_search_depth"
            ]

            if g.user_id in g.couch:
                _my_document = g.couch[g.user_id]

                if "settings" in _my_document:
                    _opponent_type = _my_document["settings"]["friendly"][
                        "opponent_type"
                    ]
                    _league_search_depth = _my_document["settings"]["friendly"][
                        "league_search_depth"
                    ]

            sl = helperf.get_series_list(
                g.flagid, search_level=int(_league_search_depth)
            )

            ctl = helperf.get_challengeable_teams_list(session["teamid"], sl)

            for team in ctl:
                _xml = api.ht_get_data("teamdetails", teamID=team, includeFlags="false")
                _team = api.ht_get_team(_xml)

                if _opponent_type == "all":
                    _team = (team, _team[team]["team_name"])
                    g.challengeable.append(_team)

                else:
                    signup_year = _team["user"]["signup_date"].split("-", 1)[0]
                    actual_year = datetime.now().year

                    if (
                        _team["user"]["supporter_tier"] != "none"
                        and int(actual_year) - int(signup_year) > 0
                    ):
                        _team = (team, _team[team]["team_name"])
                        g.challengeable.append(_team)

        session["challengeable"] = g.challengeable

    return render_template("flags/details.html")
