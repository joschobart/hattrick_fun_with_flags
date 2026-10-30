"""Men's opponent search: stops at 25 teams and counts stats."""

import base64

from fun_with_flags import helperf


def _fake_chpp(monkeypatch, calls):
    def fake_get_data(name, **p):
        calls.append(name if name != "teams_in_series" else p["leagueLevelUnitID"])
        if name == "teams_in_series":
            return p["leagueLevelUnitID"]
        if name == "challengeable_teams":
            return p["suggestedTeamIds"]
        return p["teamID"]  # teamdetails

    monkeypatch.setattr(helperf.api, "ht_get_data", fake_get_data)
    # 8 teams per series, like a real Hattrick series
    monkeypatch.setattr(helperf.api, "ht_get_teams_in_series",
                        lambda s: {"series_teams": [f"{s}-{i}" for i in range(8)]})
    # CHPP says "yes" to everyone
    monkeypatch.setattr(helperf.api, "ht_get_challengeable_teams", lambda x: x.split(", "))
    monkeypatch.setattr(helperf.api, "ht_get_team", lambda t: {
        "user": {"last_login_date": "2099-01-01 00:00:00",
                 "signup_date": "2020-01-01", "supporter_tier": "gold"},
        t: {"team_name": f"Team {t}"},
    })


def test_men_search_stops_after_25_teams(monkeypatch):
    calls = []
    _fake_chpp(monkeypatch, calls)
    stats = {}

    result = helperf.get_challengeable_teams_list(
        "628463", "home", ["s1", "s2", "s3", "s4", "s5", "s6"], "0", "all", stats=stats
    )

    assert len(result) == 25
    # 8 + 8 + 8 = 24 after s3, the 25th team comes from s4, then return
    assert "s5" not in calls and "s6" not in calls  # no wasted requests 🎯
    assert stats == {"scanned": [], "checked": 32, "chpp_yes": 32}


def test_men_search_all_false_is_detectable(monkeypatch):
    calls = []
    _fake_chpp(monkeypatch, calls)
    monkeypatch.setattr(helperf.api, "ht_get_challengeable_teams", lambda x: [])
    stats = {}

    result = helperf.get_challengeable_teams_list(
        "628463", "home", ["s1", "s2"], "0", "all", stats=stats
    )

    assert result == []
    assert stats == {"scanned": [], "checked": 16, "chpp_yes": 0}  # → "Hattrick says no to everyone"


def _svg(data_uri):
    return base64.b64decode(data_uri.split(",", 1)[1]).decode("utf-8")


def test_worldmap_empty_collection_shows_friendly_text():
    flags = {"3242724": {"flags_home": [], "flags_away": []}}
    svg = _svg(helperf.render_worldmap(flags, "3242724"))
    assert helperf.WORLDMAP_NO_DATA_TEXT in svg


CHALLENGEABLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<HattrickData><Team><ChallengeableResult>
  <Opponent><IsChallengeable>False</IsChallengeable><UserId>10148773</UserId>
    <TeamId>3231566</TeamId><TeamName>Ladys Blau Weiss</TeamName></Opponent>
  <Opponent><IsChallengeable>False</IsChallengeable><UserId>0</UserId>
    <TeamId>3219012</TeamId><TeamName>Punane Esmaspäev</TeamName></Opponent>
</ChallengeableResult></Team></HattrickData>"""


def test_scanned_opponents_skips_bots_and_keeps_names():
    assert helperf._scanned_opponents(CHALLENGEABLE_XML) == [("3231566", "Ladys Blau Weiss")]


def test_scanned_collects_all_and_samples_random_40(monkeypatch):
    def fake_get_data(name, **p):
        ids = p["suggestedTeamIds"].split(", ")
        return "<HattrickData>" + "".join(
            f"<Opponent><UserId>1</UserId><TeamId>{i}</TeamId><TeamName>T{i}</TeamName></Opponent>"
            for i in ids
        ) + "</HattrickData>"

    monkeypatch.setattr(helperf.api, "ht_get_data", fake_get_data)
    monkeypatch.setattr(helperf.api, "ht_get_challengeable_teams", lambda x: [])
    stats = {}
    helperf.get_challengeable_women_teams(
        "3242724", "home", [str(i) for i in range(80)], "0", "all", stats=stats)

    assert len(stats["scanned"]) == 80                     # nothing dropped
    shown = helperf.sample_scanned(stats["scanned"])
    assert len(shown) == helperf.SCANNED_MAX               # 40 for display
    assert len(set(shown)) == 40                           # no duplicates
    assert set(shown) <= set(stats["scanned"])             # only real scanned teams


def test_sample_scanned_with_few_teams():
    few = [("1", "A"), ("2", "B")]
    assert sorted(helperf.sample_scanned(few)) == few      # fewer than 40 → all of them
