""" FwF-scheduler related functions """


from datetime import datetime, timedelta

from . import api, db, helperf


def sensor():
    """Function for scheduler-job execution."""

    utc = datetime.utcnow()

    _couch = db.get_db("fwf_schedules")

    _my_doc_name = utc.strftime("%Y%m%d")

    _my_document = _couch[_my_doc_name]

    for _key in _my_document.keys():
        if _key != "_id" and _key != "_rev":
            _challengeable = []
            _team_id = _key

            if _my_document[_team_id]["fernet_token"] == "":
                continue

            else:
                _opponent_type = _my_document[_team_id]["opponent_type"]
                _fernet_token = _my_document[_team_id]["fernet_token"]
                _country_id = _my_document[_team_id]["country_id"]
                _search_depth = _my_document[_team_id]["search_depth"]
                _match_place = _my_document[_team_id]["match_place"]
                _match_rules = _my_document[_team_id]["match_rules"]
                _weekend_friendly = "0"

                if _match_place == "home":
                    _mp = "0"
                else:
                    _mp = "1"

                if _match_rules == "normal":
                    _mr = "0"
                else:
                    _mr = "1"

                _series_list = helperf.get_series_list(
                    _country_id,
                    search_level=int(_search_depth),
                    fernet_token=_fernet_token,
                )

                _challengeable = helperf.get_challengeable_teams_list(
                    _team_id,
                    _mp,
                    _series_list,
                    _weekend_friendly,
                    _opponent_type,
                    fernet_token=_fernet_token,
                )

                if len(_challengeable) == 0:
                    # re-schedule in a week if no opponent present
                    _object = {
                        "type": "add_schedule",
                        "data": {
                            "object": {
                                "team_id": _team_id,
                                "fernet_token": _fernet_token,
                                "country_id": _country_id,
                                "match_place": _match_place,
                                "match_rules": _match_rules,
                                "opponent_type": _opponent_type,
                                "search_depth": _search_depth,
                                "weekend_friendly": _weekend_friendly,
                            },
                        },
                    }
                    schedule(_object)

                else:
                    # challenge opponents if len(_challengeable) > 0
                    _challengeable = list(zip(*_challengeable))[0]

                    _challenged = api.ht_do_challenge(
                        _team_id,
                        _challengeable,
                        _mr,
                        _mp,
                        _weekend_friendly,
                        fernet_token=_fernet_token,
                    )

                    print(f"challengeable teams: {_challengeable}")
                    print(f"Challenged response: {_challenged}")

                # Finally delete fernet-token from DB
                # to mark a done transaction.
                _my_document[_team_id]["fernet_token"] = ""
                _couch[_my_doc_name] = _my_document

    return


def schedule(_event):
    """Function to life-cycle schedules in db.

    :param _event:

    """

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
            return e

        # Write success-object to cache-db
        _couch[_scheduler_date] = _cache_document

    if _event and _event["type"] == "get_schedule":
        _team_id = _event["data"]["object"]["team_id"]

        if _scheduler_date in _couch:
            _my_document = _couch[_scheduler_date]

            if _team_id in _my_document:
                if _my_document[_team_id]["fernet_token"] != "":
                    _scheduler_return_object = {
                        "date": _scheduler_date,
                        "timestamp": _my_document[_team_id]["timestamp"],
                        "country_id": _my_document[_team_id]["country_id"],
                        "match_place": _my_document[_team_id]["match_place"],
                        "match_rules": _my_document[_team_id]["match_rules"],
                        "opponent_type": _my_document[_team_id]["opponent_type"],
                        "search_depth": _my_document[_team_id]["search_depth"],
                        "weekend_friendly": _my_document[_team_id]["weekend_friendly"],
                    }

                    return _scheduler_return_object

    if _event and _event["type"] == "delete_schedule":
        _team_id = _event["data"]["object"]["team_id"]
        _fernet_token = _event["data"]["object"]["fernet_token"]

        if _scheduler_date in _couch:
            _my_document = _couch[_scheduler_date]

            if _team_id in _my_document:
                _request_fernet_decrypted = helperf.crypto_string(
                    _fernet_token, _op="decrypt"
                )
                _db_fernet_decrypted = helperf.crypto_string(
                    _my_document[_team_id]["fernet_token"], _op="decrypt"
                )

                if _request_fernet_decrypted == _db_fernet_decrypted:
                    _my_document.pop(_team_id)
                    _couch[_scheduler_date] = _my_document

    return
