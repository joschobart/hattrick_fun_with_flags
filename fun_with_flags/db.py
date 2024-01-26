import os
from datetime import datetime

import couchdb
from flask import g, session


def get_db():
    if "couch" not in g:
        couch = couchdb.Server(os.environ["COUCHDB_CONNECTION_STRING"])

        try:
            couch = couch["fwf_db"]  # existing
        except Exception as e:
            print(f"CouchDB server not available: {e}")

    return couch


def bootstrap_document(_userid, _couch, _settings):
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


def set_match_history(_userid, _couch, _worlddetails, _match_id):
    # Instantiate clone of db-document
    my_document = _couch[_userid]

    if session["teamid"] not in my_document["history"]["friendlies"]:
        my_document["history"]["friendlies"][session["teamid"]] = {
            "opponent_country": {}
        }

    if (
        _worlddetails["league_id"]
        not in my_document["history"]["friendlies"][session["teamid"]][
            "opponent_country"
        ]
    ):
        my_document["history"]["friendlies"][session["teamid"]]["opponent_country"][
            _worlddetails["league_id"]
        ] = {
            "home": [],
            "away": [],
        }

    if (
        _match_id
        not in my_document["history"]["friendlies"][session["teamid"]][
            "opponent_country"
        ][_worlddetails["league_id"]][session["place"]]
    ):
        my_document["history"]["friendlies"][session["teamid"]]["opponent_country"][
            _worlddetails["league_id"]
        ][session["place"]].append(_match_id)

        my_document["history"]["meta"]["date_updated"] = str(datetime.utcnow())

    return my_document
