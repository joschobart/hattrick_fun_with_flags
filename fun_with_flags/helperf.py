import os
from datetime import datetime
from random import randrange

from cryptography.fernet import Fernet
from flask import g, session
from pygal import maps, style

from . import api


def crypto_string(_input, _op="encrypt"):
    output = ""

    fernet = Fernet(os.environb[b"FERNET_SECRET"])

    if _op == "encrypt":
        output = fernet.encrypt(_input.encode())

    elif _op == "decrypt":
        output = fernet.decrypt(_input).decode()

    return output


def get_my_teams():
    teams = []

    for _entry in list(session["my_team"]):
        if _entry != "user":
            team = (
                _entry,
                session["my_team"][_entry]["team_name"],
                session["my_team"][_entry]["team_primary"],
            )

            teams.append(team)

    # first sort after 'team_primary', then team_id
    session["teams"] = sorted(
        teams, key=lambda _entry: (_entry[2], _entry[0]), reverse=True
    )

    if "teamid" not in session:
        session["teamid"] = session["teams"][0][0]


def compose_flag_matrix(teamid):
    xml_data = api.ht_get_data("teamdetails", teamID=teamid, includeFlags="true")

    my_flags = api.ht_get_flags(xml_data)
    my_missing_flags = api.ht_get_missing_flags(xml_data)

    base_url = "https://www.hattrick.org/Img/flags/"
    url_end_i = "_inactive.png"
    url_end = ".png"

    l_home = []
    l_away = []

    nbr_flags_home = (len(my_flags[teamid]["flags_home"]), 147)
    nbr_flags_away = (len(my_flags[teamid]["flags_away"]), 147)

    for m in (my_flags, my_missing_flags):
        for ha in m[teamid].keys():
            for flag in range(len(m[teamid][ha])):
                i = m[teamid][ha][flag][0]
                w = m[teamid][ha][flag][1]
                w = w.replace("ô", "o")
                w = w.replace("ã", "a")

                if ha == "missing_home":
                    l_home.append(
                        (i, w, (base_url + m[teamid][ha][flag][0] + url_end_i))
                    )

                elif ha == "flags_home":
                    l_home.append((i, w, (base_url + m[teamid][ha][flag][0] + url_end)))

                elif ha == "missing_away":
                    l_away.append(
                        (i, w, (base_url + m[teamid][ha][flag][0] + url_end_i))
                    )

                else:
                    l_away.append((i, w, (base_url + m[teamid][ha][flag][0] + url_end)))

    worldmap_chart = render_worldmap(my_flags, teamid)

    return l_home, l_away, nbr_flags_home, nbr_flags_away, worldmap_chart


def get_series_list(flagid, search_level=2):
    probe_list = []
    series_list = []

    league_table = [
        (2, "ii", 4),
        (3, "iii", 16),
        (4, "iv", 64),  # <------ default (search_level=2)
        (
            5,
            "v",
            256,
        ),  # <------ 340 series, max. 2720 teams (deep-search)
        (6, "vi", 1024),
    ]

    league_depth = api.ht_get_data("worlddetails", leagueID=flagid)
    league_depth = api.ht_get_worlddetails(league_depth)

    def get_series_id(search_string, flagid):
        api_response = api.ht_get_data(
            "search_series", searchString=search_string, searchLeagueID=flagid
        )

        probe_list.append(api.ht_get_series(api_response)["series_id"])

        return probe_list

    # Here the depth of
    # the loop is adjustable
    for l_tuple in league_table[0:search_level]:
        if l_tuple[0] > int(league_depth["league_depth"]):
            break

        l_numbers = 1, l_tuple[2]

        for l_number in l_numbers:
            get_series_id(f"{l_tuple[1]}.{l_number}", flagid)

        lid_difference = int(probe_list[1]) - int(probe_list[0])
        l_difference = l_tuple[2] - 1

        if lid_difference != l_difference:
            print(
                "WARNING: anomaly in leagueID numbering found. do pricy loops as fallback."
            )
            # not integrated yet

        else:
            for i in range(int(probe_list[0]), int(probe_list[1]) + 1):
                series_list.append(i)

        probe_list.clear()

    return series_list


def get_challengeable_teams_list(teamid, series_list):
    for series in series_list:
        teams_in_series = api.ht_get_data("teams_in_series", leagueLevelUnitID=series)
        teams_in_series = api.ht_get_teams_in_series(teams_in_series)
        teams_in_series = ", ".join(teams_in_series["series_teams"])

        challengeable_teams = api.ht_get_data(
            "challengeable_teams",
            teamId=teamid,
            matchPlace=session["place"],
            suggestedTeamIds=teams_in_series,
        )

        challengeable_teams = api.ht_get_challengeable_teams(challengeable_teams)

        for team in challengeable_teams:
            yield team


def get_my_challenges():
    now = datetime.now()
    utc = datetime.utcnow()

    challenges = []
    match_time = ""
    tdelta = ""
    tdelta_hours = ""
    bookable = False

    _teamid = session.get("teamid", None)

    _xml = api.ht_get_data("get_challenges", teamId=_teamid)

    challenges = api.ht_get_challenges(_xml)
    print(challenges["challenges"])

    if 0 < len(challenges["challenges"]) < 25:
        bookable = True

    if challenges["challenges"] != []:
        if challenges["challenges"][0]["is_agreed"] == "True":
            bookable = False

        match_time = challenges["challenges"][0]["match_time"]
        match_time = datetime.strptime(match_time, "%Y-%m-%d %H:%M:%S")
        tdelta = match_time - now
        tdelta = tdelta.total_seconds()
        tdelta_hours = round(tdelta / 3600, 1)

    else:
        if (
            utc.weekday() == 3
            and utc.hour >= 7
            or utc.weekday() >= 4
            or utc.weekday() == 0
        ):
            bookable = True

    return challenges, now, match_time, tdelta, tdelta_hours, bookable


def random_quotes(_quotes):
    for _key in _quotes.keys():
        random_quote_index = randrange(0, len(_quotes[_key]))

        if _key == "quotes_ante":
            quote_ante = _quotes[_key][random_quote_index]
        else:
            quote_post = _quotes[_key][random_quote_index]

    return quote_ante, quote_post


def render_worldmap(flaglist, teamid):
    my_flags = flaglist
    teamid = teamid

    map_flags_home = []
    map_flags_away = []
    map_flags_both = []

    _style = style.Style(
        foreground="#53E89B",
        foreground_strong="#311D3F",
        foreground_subtle="#522546",
        opacity=".6",
        opacity_hover=".9",
        transition="400ms ease-in",
        colors=("#40513B", "#609966", "#522546", "#88304E"),
    )

    worldmap_chart = maps.world.World(height=350, style=_style)

    for home_flag in my_flags[teamid]["flags_home"]:
        home_flag = home_flag[2].lower()

        map_flags_home.append(home_flag)

    for away_flag in my_flags[teamid]["flags_away"]:
        away_flag = away_flag[2].lower()

        map_flags_away.append(away_flag)

    for home_flag in map_flags_home:
        if home_flag in map_flags_away:
            map_flags_both.append(home_flag)

            home_flag_index = map_flags_home.index(home_flag)
            away_flag_index = map_flags_away.index(home_flag)

            map_flags_home.pop(home_flag_index)
            map_flags_away.pop(away_flag_index)

    worldmap_chart.add("Home Flags", map_flags_home)
    worldmap_chart.add("Away Flags", map_flags_away)
    worldmap_chart.add("Both Flags", map_flags_both)

    worldmap_chart = worldmap_chart.render_data_uri()

    return worldmap_chart
