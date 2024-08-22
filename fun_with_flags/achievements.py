"""FwF achievements view"""

from datetime import datetime
from time import strftime

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

    _flags_per_team = []
    for _team in session["my_team"].keys():
        if _team == "user":
            continue

        _nr_flags_home = 0
        _nr_flags_away = 0
        (
            g.l_home,
            g.l_away,
            nr_flags_home,
            nr_flags_away,
            *_,
        ) = helperf.compose_flag_matrix(_team)
        _nr_flags_home += nr_flags_home[0]
        _nr_flags_away += nr_flags_away[0]
        _total_nr_flags = _nr_flags_home + _nr_flags_away
        _flags_per_team.append((_team, _total_nr_flags))

    _total_of_flags = 0
    for _team in _flags_per_team:
        _total_of_flags += _team[1]

    g.avg_flag_count_per_team = int(round(_total_of_flags / len(_flags_per_team), 0))

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

    g.unicorn_score = 0
    try:
        for _pay_session in _my_document["unicorn"]["stripe"]["sessions"]:
            if (
                "receipt_timestamp"
                in _my_document["unicorn"]["stripe"]["sessions"][_pay_session]
            ):
                _my_pay_session = _my_document["unicorn"]["stripe"]["sessions"][
                    _pay_session
                ]
                _amount = float(_my_pay_session["receipt_amount_received"])
                _factor = float(_my_pay_session["receipt_factor"])
                g.unicorn_score += int(round(_amount * _factor))
    except KeyError:
        pass

    g.fun_with_flags_score = (
        g.avg_flag_count_per_team
        + g.unicorn_score
        + g.fwf_matches_home
        + g.fwf_matches_away
    )
    _weeknumber = strftime("%W")

    _my_document["score"]["score"] = g.fun_with_flags_score
    _my_document["score"]["history"][_weeknumber] = g.fun_with_flags_score
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
                _score_list.append((_couchdoc["key"], _score))

    _score_list = sorted(_score_list, key=lambda x: x[1], reverse=True)
    _position = [x[1] for x in _score_list].index(g.fun_with_flags_score) + 1
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
