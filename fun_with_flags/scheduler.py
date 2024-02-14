""" View to customize schedules for FwF. """

from datetime import datetime, timedelta

from flask import g, jsonify

from . import db, helperf


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

            if _my_document[team_id]["fernet_token"] == "":
                continue
            else:
                opponent_type = _my_document[team_id]["opponent_type"]
                fernet_token = _my_document[team_id]["fernet_token"]
                country_id = _my_document[team_id]["country_id"]
                search_depth = _my_document[team_id]["search_depth"]
                match_place = _my_document[team_id]["match_place"]
                match_rules = _my_document[team_id]["match_rules"]
                weekend_friendly = "0"

                if match_place == "home":
                    match_place = "0"
                else:
                    match_place = "1"

                if match_rules == "normal":
                    match_rules = "0"
                else:
                    match_rules = "1"

                series_list = helperf.get_series_list(
                    country_id,
                    search_level=int(search_depth),
                    fernet_token=fernet_token,
                )

                _challengeable = helperf.get_challengeable_teams_list(
                    team_id,
                    match_place,
                    series_list,
                    weekend_friendly,
                    opponent_type,
                    fernet_token=fernet_token,
                )

                # WIP : challenge logic is still missing here

                # Finally delete fernet-token from DB
                # to mark a successful transaction.
                _my_document[team_id]["fernet_token"] = ""
                _couch[_my_doc_name] = _my_document

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

    if _event and _event["type"] == "get_schedule":
        _team_id = _event["data"]["object"]["team_id"]

        if _scheduler_date in _couch:
            _my_document = _couch[_scheduler_date]

            if _team_id in _my_document:
                if _my_document[_team_id]["fernet_token"] != "":
                    g.scheduler_return_object = {
                        "date": _scheduler_date,
                        "timestamp": _my_document[_team_id]["timestamp"],
                        "country_id": _my_document[_team_id]["country_id"],
                        "match_place": _my_document[_team_id]["match_place"],
                        "match_rules": _my_document[_team_id]["match_rules"],
                        "opponent_type": _my_document[_team_id]["opponent_type"],
                        "search_depth": _my_document[_team_id]["search_depth"],
                        "weekend_friendly": _my_document[_team_id]["weekend_friendly"],
                    }

                    return g.scheduler_return_object

    if _event and _event["type"] == "delete_schedule":
        _team_id = _event["data"]["object"]["team_id"]
        _fernet_token = _event["data"]["object"]["fernet_token"]

        if _scheduler_date in _couch:
            _my_document = _couch[_scheduler_date]

            if _team_id in _my_document:
                if _my_document[_team_id]["fernet_token"] == _fernet_token:
                    _my_document.pop(_team_id)
                    _couch[_scheduler_date] = _my_document

    return jsonify(success=True)
