"""Men's opponent search: stops at 25 teams and counts stats."""

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
    assert stats == {"checked": 32, "chpp_yes": 32}


def test_men_search_all_false_is_detectable(monkeypatch):
    calls = []
    _fake_chpp(monkeypatch, calls)
    monkeypatch.setattr(helperf.api, "ht_get_challengeable_teams", lambda x: [])
    stats = {}

    result = helperf.get_challengeable_teams_list(
        "628463", "home", ["s1", "s2"], "0", "all", stats=stats
    )

    assert result == []
    assert stats == {"checked": 16, "chpp_yes": 0}  # → "Hattrick says no to everyone"
