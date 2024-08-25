"""FwF achievements view"""

from datetime import datetime
from time import strftime

import pygal
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
    _weeknumber = strftime("%Y%W")

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


    _neighbors = {g.user_id: {}}
    try:
        for x in range(_position, (_position + 4)):
            _neighbors[_score_list[x][0]] = {}
    except IndexError:
        pass

    for x in range((_position - 4), _position):
        if x <= 0:
            continue
        _neighbors[_score_list[x][0]] = {}


    line_chart = pygal.Line()
    line_chart.title = 'Your FwF Neighbors Score Evolution'


    _weeks = set()
    for _neighbor in _neighbors:
        _my_neighbor_doc = _couch[_neighbor]
        try:
            _neighbors[_neighbor] = _my_neighbor_doc["score"]["history"]

            _weeks.update(_my_neighbor_doc["score"]["history"].keys())

        except KeyError:
            continue

    _weeks = sorted(_weeks)


    for _neighbor in _neighbors:
        _scores = []
        _my_neighbor_doc = _couch[_neighbor]

        for _week in range(int(_weeks[0]), int(_weeks[-1]) + 1):
            try:
                _scores.append(_my_neighbor_doc["score"]["history"][str(_week)])
            except Exception:
                _scores.append(None)
        
        if not "history" in _my_neighbor_doc["score"].keys():
            _scores[-1] = _my_neighbor_doc["score"]["score"]
            _scores[-2] = _my_neighbor_doc["score"]["score"]
        elif len(_my_neighbor_doc["score"]["history"].keys()) < 2:
            _scores[-2] = _my_neighbor_doc["score"]["score"]
        else:
            pass

        if _scores[-1] is None:
            _scores[-1] = _my_neighbor_doc["score"]["score"]           

        if _neighbor == g.user_id:
            line_chart.add("You", _scores)
        else:
            line_chart.add(_neighbor, _scores)


    line_chart.x_labels = map(str, range(int(_weeks[0]), int(_weeks[-1])))
    line_chart = line_chart.render_data_uri()


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


    return render_template("achievements/achievements.html", line_chart=line_chart)
