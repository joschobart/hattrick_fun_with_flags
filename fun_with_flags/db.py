import os
from datetime import datetime

import couchdb
from flask import g, session


def bootstrap_generic_document(_id, _couch, _object, _namespace="payload"):
    # Bootstrap db-document if it doesn't exist
    if _id not in _couch:
        _couch.save({"_id": _id})

    # Instantiate clone of db-document
    db_document = _couch[_id]

    db_document[_namespace] = _object

    return db_document


def bootstrap_user_document(_userid, _couch, _settings):
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
    couch = couchdb.Server(os.environ["COUCHDB_CONNECTION_STRING"])

    try:
        couch = couch[_couch]  # existing

    except Exception as e:
        print(f"CouchDB server not available: {e}")

    return couch


def get_unicorn_state():
    if "user_id" in g:
        _userid = g.user_id
        _couch = g.couch
    else:
        _userid = session["my_team"]["user"]["user_id"]
        _couch = get_db()

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

    return is_unicorn


def set_match_history(_userid, _couch, _league_id, _match_id, _place):
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
    # Instantiate clone of db-document
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
