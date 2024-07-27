""" couch-db related functions """


import os
from datetime import datetime
from time import sleep

import couchdb
from flask import g, session

from . import api


def bootstrap_generic_document(_id, _couch, _object, _namespace="payload"):
    """

    :param _id:
    :param _couch:
    :param _object:
    :param _namespace:  (Default value = "payload")

    """
    # Bootstrap db-document if it doesn't exist
    if _id not in _couch:
        _couch.save({"_id": _id})

    # Instantiate clone of db-document
    db_document = _couch[_id]

    db_document[_namespace] = _object

    return db_document


def bootstrap_user_document(_userid, _couch, _settings):
    """

    :param _userid:
    :param _couch:
    :param _settings:

    """
    # Bootstrap db-document if it doesn't exist
    if _userid not in _couch:
        _couch.save({"_id": _userid})

    # Instantiate clone of db-document
    db_document = _couch[_userid]

    for _key in _settings.keys():
        if _key != "defaults":
            # Bootstrap objects in document if they don't exist yet
            if _key not in db_document:
                db_document[_key] = {"meta": _settings[_key]["meta"]}
                db_document[_key]["meta"]["date_initialized"] = str(datetime.utcnow())

                for _subkey in _settings[_key]:
                    if _subkey != "meta":
                        db_document[_key][_subkey] = {}

                        for _subsubkey in _settings["defaults"][_key][_subkey].keys():
                            db_document[_key][_subkey][_subsubkey] = _settings[
                                "defaults"
                            ][_key][_subkey][_subsubkey]

            # Update object if schema was updated
            if (
                db_document[_key]["meta"]["schema_version"]
                < _settings[_key]["meta"]["schema_version"]
            ):
                for _object in _settings[_key].items():
                    if _object[0] != "meta":
                        if _object[0] not in db_document[_key]:
                            db_document[_key][_object[0]] = {}
                            db_document[_key]["meta"]["date_updated"] = str(
                                datetime.utcnow()
                            )

                        for _k, _v in _settings["defaults"][_key][_object[0]].items():
                            if _k not in db_document[_key][_object[0]]:
                                db_document[_key][_object[0]][_k] = _settings[
                                    "defaults"
                                ][_key][_object[0]][_k]
                                db_document[_key]["meta"]["date_updated"] = str(
                                    datetime.utcnow()
                                )

                db_document[_key]["meta"]["schema_version"] = _settings[_key]["meta"][
                    "schema_version"
                ]

    return db_document


def get_db(_couch="fwf_db"):
    """

    :param _couch:  (Default value = "fwf_db")

    """
    couch = couchdb.Server(os.environ["COUCHDB_CONNECTION_STRING"])

    try:
        couch = couch[_couch]  # existing

    except Exception as e:
        print(f"CouchDB server not available: {e}")

    return couch


def get_unicorn_state():
    """ """
    if "user_id" in g:
        _userid = g.user_id
        _couch = g.couch
    else:
        _userid = session["my_team"]["user"]["user_id"]
        _couch = get_db()

    if _userid in _couch:
        _my_document = _couch[_userid]

        if "unicorn" in _my_document:
            try:
                is_unicorn = _my_document["unicorn"]["unicorn"]
            except Exception:
                is_unicorn = False
            else:
                if is_unicorn == "True":
                    is_unicorn = True
                else:
                    is_unicorn = False
        else:
            is_unicorn = False
    else:
        is_unicorn = False

    return is_unicorn


def get_language():
    """ """
    if "user_id" in g:
        _userid = g.user_id
        _couch = g.couch
    else:
        _userid = session["my_team"]["user"]["user_id"]
        _couch = get_db()

    if _userid in _couch:
        _my_document = _couch[_userid]

        if "settings" in _my_document:
            try:
                language = _my_document["settings"]["locale"]["language"]
            except Exception:
                language = "None"

    return language


def get_settings(_userid, _couch, _settings):
    """

    :param _userid:
    :param _couch:
    :param _settings:

    """
    _my_document = g.couch[g.user_id]

    # Set opponent_type for match and league_search_depth
    # from config and overwrite if custom config is available in db.

    _opponent_type = _settings["defaults"]["settings"]["friendly"]["opponent_type"]
    _league_search_depth = _settings["defaults"]["settings"]["friendly"][
        "league_search_depth"
    ]
    _match_rules = _settings["defaults"]["settings"]["friendly"]["match_rules"]

    if "settings" in _my_document:
        _opponent_type = _my_document["settings"]["friendly"]["opponent_type"]
        _match_rules = _my_document["settings"]["friendly"]["match_rules"]
        _league_search_depth = _my_document["settings"]["friendly"][
            "league_search_depth"
        ]
    return (_opponent_type, _match_rules, _league_search_depth)


def get_match_history(_userid, _couch, _flagid, _place):
    """

    :param _userid:
    :param _couch:
    :param _flagid:
    :param _place:

    """
    _my_document = _couch[_userid]

    if "history" in _my_document:
        _played_matches = []

        if session["teamid"] in _my_document["history"]["friendlies"]:
            if (
                _flagid
                in _my_document["history"]["friendlies"][session["teamid"]][
                    "opponent_country"
                ]
            ):
                for _match in _my_document["history"]["friendlies"][session["teamid"]][
                    "opponent_country"
                ][_flagid][_place]:
                    _xml_data = api.ht_get_data(
                        "matchdetails", teamID=session["teamid"], matchID=_match
                    )
                    _my_match = api.ht_get_matchdetails(_xml_data)
                    _match_date = datetime.strptime(
                        _my_match["match_date"], "%Y-%m-%d %H:%M:%S"
                    )
                    _timedelta = datetime.now() - _match_date
                    _timedelta = _timedelta.total_seconds()

                    if _timedelta > 0:
                        _match_date = _match_date.strftime("%d.%m.%Y %H:%M")
                        _my_match["match_date"] = _match_date
                        _played_matches.append(_my_match)

                    if _my_match["match_type"] == "4" or _my_match["match_type"] == "8":
                        _my_match["match_type"] = "Friendly (normal rules)"
                    elif (
                        _my_match["match_type"] == "5" or _my_match["match_type"] == "9"
                    ):
                        _my_match["match_type"] = "Friendly (cup rules)"

            _played_matches = sorted(
                _played_matches, key=lambda x: x["match_id"], reverse=True
            )

        return _played_matches


def set_match_history(_userid, _couch, _league_id, _match_id, _place):
    """

    :param _userid:
    :param _couch:
    :param _league_id:
    :param _match_id:
    :param _place:

    """
    # Instantiate clone of db-document
    my_document = _couch[_userid]

    if session["teamid"] not in my_document["history"]["friendlies"]:
        my_document["history"]["friendlies"][session["teamid"]] = {
            "opponent_country": {}
        }

    if (
        _league_id
        not in my_document["history"]["friendlies"][session["teamid"]][
            "opponent_country"
        ]
    ):
        my_document["history"]["friendlies"][session["teamid"]]["opponent_country"][
            _league_id
        ] = {
            "home": [],
            "away": [],
        }

    if (
        _match_id
        not in my_document["history"]["friendlies"][session["teamid"]][
            "opponent_country"
        ][_league_id][_place]
    ):
        my_document["history"]["friendlies"][session["teamid"]]["opponent_country"][
            _league_id
        ][_place].append(_match_id)

        my_document["history"]["meta"]["date_updated"] = str(datetime.utcnow())

    return my_document


def init_stripe_session(_userid, _couch, _stripe_user, _session_id, _transaction_id):
    """

    :param _userid:
    :param _couch:
    :param _stripe_user:
    :param _session_id:
    :param _transaction_id:

    """
    # Instantiate clone of db-document
    my_document = _couch[_userid]

    if "stripe_user" not in my_document["unicorn"]["stripe"]:
        my_document["unicorn"]["stripe"]["stripe_user"] = _stripe_user
        my_document["unicorn"]["stripe"]["sessions"] = {}

    my_document["unicorn"]["stripe"]["sessions"][_session_id] = {
        "date_initialized": str(datetime.utcnow()),
        "initialisation_id": _transaction_id,
    }

    my_document["unicorn"]["meta"]["date_updated"] = str(datetime.utcnow())

    return my_document


def close_stripe_session(_userid, _couch, _session_id):
    """

    :param _userid:
    :param _couch:
    :param _session_id:

    """
    # sleep 3 secs as stripe sometimes needs time to submit to the webhook
    sleep(3)

    # instantiate clone of db-document
    my_document = _couch[_userid]

    _stripe_user = my_document["unicorn"]["stripe"]["stripe_user"]
    _cache_couch = get_db("fwf_cache")

    if _stripe_user in _cache_couch:
        my_cache_document = _cache_couch[_stripe_user]

        for _key in my_cache_document["payload"]:
            my_document["unicorn"]["stripe"]["sessions"][_session_id][
                f"receipt_{_key}"
            ] = my_cache_document["payload"][_key]

        my_document["unicorn"]["unicorn"] = "True"

        _cache_couch.delete(my_cache_document)

    else:
        my_document["unicorn"]["stripe"]["sessions"][_session_id][
            "cancel_timestamp"
        ] = str(datetime.utcnow())

        if not my_document["unicorn"]["unicorn"] == "True":
            my_document["unicorn"]["unicorn"] = "False"

    my_document["unicorn"]["meta"]["date_updated"] = str(datetime.utcnow())

    return my_document
