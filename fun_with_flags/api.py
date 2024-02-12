from flask import session
from ht_libs import (
    do_challenge,
    do_hattrick_request,
    get_flags,
    get_matchdetails,
    get_matches,
    get_series,
    get_teamdetails,
    get_trainer_avatar,
    get_worlddetails,
)

from . import helperf

API_URL = "https://chpp.hattrick.org/chppxml.ashx"

API_PARAMS = {
    "teamdetails": {
        "file": "teamdetails",
        "version": "3.6",
        "teamID": "",
        "includeFlags": "",
    },
    "search_series": {
        "file": "search",
        "version": "1.2",
        "searchType": "3",
        "searchString": "ii.1",  # e.g.: ii.1 for series II.1
        "searchLeagueID": "",  # e.g.: 46 for switzerland
    },
    "worlddetails": {
        "file": "worlddetails",
        "version": "1.9",
        "includeRegions": "false",
        "countryID": "",
        "leagueID": "",
    },
    "teams_in_series": {
        "file": "leaguedetails",
        "version": "1.6",
        "leagueLevelUnitID": "false",
    },
    "challengeable_teams": {
        "file": "challenges",
        "version": "1.6",
        "actionType": "challengeable",
        "teamId": "",  # id of team to manage
        "matchType": "1",  # 0 = normal, 1 = cup-rules
        "matchPlace": "",  # 0 = home, 1 = away
        "suggestedTeamIds": "",  # CSV list of TeamIds
        "isWeekendFriendly": "",  # 0 = normal, 1 = weekend
    },
    "get_challenges": {
        "file": "challenges",
        "version": "1.6",
        "actionType": "view",
        "teamId": "",  # id of team to manage
        "isWeekendFriendly": "0",
    },
    "get_trainer_avatar": {
        "file": "staffavatars",
        "version": "1.1",
        "teamId": "",
    },
    "matchdetails": {
        "file": "matchdetails",
        "version": "3.1",
        "matchEvents": "false",
        "matchID": "",  # id of match to get
        "sourceSystem": "hattrick",
    },
    "get_matches": {
        "file": "matches",
        "version": "2.9",
        "teamID": "",
    },
}


def ht_do_challenge(
    teamid, challengeable_teams_list, match_type, match_place, weekend_friendly
):
    ht_session = oauth_open_session()

    my_challenges = do_challenge.do_challenge(
        teamid,
        ht_session,
        challengeable_teams_list,
        match_type,
        match_place,
        weekend_friendly,
    )

    return my_challenges


def ht_get_challengeable_teams(challengeable_xml):
    challengeable_teams_list = do_challenge.is_challengeable(challengeable_xml)

    return challengeable_teams_list


def ht_get_challenges(challenges_xml):
    challenges = do_challenge.get_challenges(challenges_xml)

    return challenges


def ht_get_data(name, api_url=API_URL, fernet_token="", **kwargs):
    if fernet_token == "":
        try:
            fernet_token = session["encrypted_access_token"]
        except Exception as e:
            print(f"{e}: No Session context and fernet token.")

    ht_session = oauth_open_session(fernet_token)

    params = API_PARAMS[name]
    params.update(kwargs)
    print(params)

    xml_data = ht_session.get(api_url, params=params)
    xml_data = (
        str(xml_data.text)
        .encode("latin1")
        .decode("unicode_escape")
        .encode("latin1")
        .decode("utf8")
    )

    return xml_data


def ht_get_flags(teamdetails_xml):
    flags_dict = get_flags.get_my_flags(teamdetails_xml)

    return flags_dict


def ht_get_matchdetails(matchdetails_xml):
    matchdetails = get_matchdetails.get_matchdetails(matchdetails_xml)

    return matchdetails


def ht_get_matches(matches_xml):
    matches = get_matches.get_matches(matches_xml)

    return matches


def ht_get_missing_flags(teamdetails_xml):
    missing_flags_dict = get_flags.get_missing_flags(teamdetails_xml)

    return missing_flags_dict


def ht_get_series(search_series_xml):
    series_dict = get_series.get_my_series(search_series_xml)

    return series_dict


def ht_get_team(xml_data):
    team_dict = get_teamdetails.get_teamdetails(xml_data)

    return team_dict


def ht_get_teams_in_series(teams_in_series_xml):
    teams_dict = get_series.get_teams_in_series(teams_in_series_xml)

    return teams_dict


def ht_get_trainer_avatar(staffavatars_xml):
    trainer_avatar = get_trainer_avatar.get_trainer_avatar(staffavatars_xml)

    return trainer_avatar


def ht_get_worlddetails(worlddetails_xml):
    worlddetails_dict = get_worlddetails.get_my_worlddetails(worlddetails_xml)

    return worlddetails_dict


def oauth_get_access_token(pin):
    access_token_key, access_token_secret = do_hattrick_request.get_access_token(
        session["request_token"],
        session["request_token_secret"],
        pin,
    )

    session.pop("request_token", None)
    session.pop("request_token_secret", None)

    return access_token_key, access_token_secret


def oauth_get_url(scope="manage_challenges"):
    (
        session["request_token"],
        session["request_token_secret"],
        authorize_url,
    ) = do_hattrick_request.fetch_authorize_url(scope=scope)

    return authorize_url


def oauth_open_session(fernet_token=""):
    try:
        creds = helperf.crypto_string(fernet_token, "decrypt")
    except Exception as e:
        print(f"{e}: Fernet token missing or invalid.")

    access_token_key = creds.split(" ", 1)[0]
    access_token_secret = creds.split(" ", 1)[1]

    ht_session = do_hattrick_request.open_auth_session(
        access_token_key,
        access_token_secret,
    )

    return ht_session
