"""FwF achievements view"""

from datetime import datetime

from flask import Blueprint, current_app, flash, g, render_template, session
from flask_babel import gettext

from . import db, decs, helperf

bp_a = Blueprint("achievements", __name__, url_prefix="/achievements")


@bp_a.route("/achievements", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_config_from_db
@decs.error_check
def achievements():
    """ """
    _db_settings = current_app.config["DB__SETTINGS_DICT"]
    _my_document = db.bootstrap_user_document(g.user_id, g.couch, _db_settings)
    _couch = db.get_db("fwf_db")
    _couchdocs = _couch.view("_all_docs")

    g.nr_flags_home = 0
    g.nr_flags_away = 0
    for _team in session["my_team"].keys():
        if _team == "user":
            continue
        (
            g.l_home,
            g.l_away,
            nr_flags_home,
            nr_flags_away,
            *_,
        ) = helperf.compose_flag_matrix(_team)
        g.nr_flags_home += nr_flags_home[0]
        g.nr_flags_away += nr_flags_away[0]

    g.fwf_matches_home = 0
    g.fwf_matches_away = 0
    try:
        for _key in _my_document["history"]["friendlies"].keys():
            for _place in "home", "away":
                for _id in range(1, 200):
                    try:
                        _matches = _my_document["history"]["friendlies"][_key][
                            "opponent_country"
                        ][str(_id)][_place]
                    except KeyError:
                        continue
                    else:
                        if _place == "home":
                            g.fwf_matches_home += len(_matches)
                        else:
                            g.fwf_matches_away += len(_matches)
    except KeyError:
        pass

    if session["unicorn"]:
        g.unicorn_score = 5
    else:
        g.unicorn_score = 0

    g.fun_with_flags_score = (
        g.nr_flags_home
        + g.nr_flags_away
        + g.unicorn_score
        + g.fwf_matches_home
        + g.fwf_matches_away
    )

    _my_document["score"]["score"] = g.fun_with_flags_score
    _my_document["score"]["meta"]["date_updated"] = str(datetime.utcnow())

    # Write changements of the score to db
    _couch[g.user_id] = _my_document

    _score_list = []
    for _couchdoc in _couchdocs:
        if not str(_couchdoc["key"]).isdigit():
            continue

        try:
            _score = _couch[_couchdoc["key"]]["score"]["score"]
        except KeyError:
            pass
        else:
            if isinstance(_score, int):
                _score_list.append(_score)

    _position = sorted(_score_list, reverse=True).index(g.fun_with_flags_score) + 1
    _competitors = len(_score_list)

    if _position <= (_competitors / 3) or _competitors < 3:
        _message = gettext("Well done!")
    elif _position <= (_competitors / 3 * 2):
        _message = gettext("There is still room to improve.")
    else:
        _message = gettext("We can do better!")

    _message = _message + gettext(
        " Your score puts you on position %(_position)s out of %(_competitors)s competitors.",
        _position=_position,
        _competitors=_competitors,
    )
    flash(_message)

    return render_template("achievements/achievements.html")
