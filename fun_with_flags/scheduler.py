""" View to customize schedules for FwF. """

from datetime import datetime, timedelta

from flask import Blueprint, jsonify

from . import db, decs, helperf

bp_s = Blueprint("scheduler", __name__, url_prefix="/scheduler")


def sensor():
    """Function for regular job execution."""

    utc = datetime.utcnow()

    _couch = db.get_db("fwf_schedules")

    _my_doc_name = utc.strftime("%Y%m%d")

    _my_document = _couch[_my_doc_name]

    for _key in _my_document.keys():
        if _key != "_id" and _key != "_rev":
            _challengeable = []
            team_id = _key
            opponent_type = _my_document[team_id]["opponent_type"]
            fernet_token = _my_document[team_id]["fernet_token"]
            country_id = _my_document[team_id]["country_id"]
            search_depth = _my_document[team_id]["search_depth"]

            sl = helperf.get_series_list(
                country_id, search_level=int(search_depth), fernet_token=fernet_token
            )

            _challengeable = helperf.get_challengeable_teams_list(
                team_id,
                _my_document[_key]["match_place"],
                sl,
                "0",
                opponent_type,
                fernet_token=fernet_token,
            )

            print(f"challengeable teams: {_challengeable}")

    return


def schedule(_event):
    # find date of next schedule run (thursday, 8utc)
    utc = datetime.utcnow()
    t = timedelta((7 + 3 - utc.weekday()) % 7)

    if t == timedelta(0) and utc.hour >= 7:
        t = timedelta(7)

    _scheduler_date = (utc + t).strftime("%Y%m%d")

    _couch = db.get_db("fwf_schedules")

    # Handle the succeeded event
    if _event and _event["type"] == "add_schedule":
        _schedule_details = _event["data"]["object"]

        _object = {
            "timestamp": str(datetime.utcnow()),
            "fernet_token": _schedule_details["fernet_token"],
            "country_id": _schedule_details["country_id"],
            "match_place": _schedule_details["match_place"],
            "match_rules": _schedule_details["match_rules"],
            "opponent_type": _schedule_details["opponent_type"],
            "search_depth": _schedule_details["search_depth"],
            "weekend_friendly": _schedule_details["weekend_friendly"],
        }

        try:
            _cache_document = db.bootstrap_generic_document(
                _scheduler_date, _couch, _object, _schedule_details["team_id"]
            )
        except Exception as e:
            print("  Api error while calling couchdb." + str(e))
            return jsonify(success=False)

        # Write success-object to cache-db
        _couch[_scheduler_date] = _cache_document

    return jsonify(success=True)
