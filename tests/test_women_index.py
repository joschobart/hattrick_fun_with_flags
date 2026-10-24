"""Women's index: bot filter and candidate lookup (no CHPP, no CouchDB)."""

from fun_with_flags import women_index, helperf

# structure as in real leaguedetails 1.6 (UserId per team), values made up
SERIES_XML = """<HattrickData><LeagueID>3000</LeagueID>
<Team><UserId>1736150</UserId><TeamID>111</TeamID></Team>
<Team><UserId>0</UserId><TeamID>222</TeamID></Team>
<Team><UserId>9034788</UserId><TeamID>333</TeamID></Team>
</HattrickData>"""


def test_human_teams_skips_bots():
    assert women_index.human_teams(SERIES_XML) == ["111", "333"]


def test_candidates_excludes_own_team(monkeypatch):
    class FakeDB:
        def get(self, doc_id):
            return {"teams": ["111", "333", "444"]} if doc_id == "flag_46" else None

    monkeypatch.setattr(women_index, "_db", lambda: FakeDB())
    assert sorted(women_index.candidates("46", exclude={"333"})) == ["111", "444"]
    assert women_index.candidates("52") == []


def test_women_search_is_a_module_function_and_filters(monkeypatch):
    challengeable_xml = "CHALLENGEABLE"

    def fake_get_data(name, **params):
        if name == "challengeable_teams":
            return challengeable_xml
        return params["teamID"]  # teamdetails: pass the id through

    def fake_team(team_id):
        return {
            "user": {
                "last_login_date": "2099-01-01 00:00:00",  # "just logged in"
                "signup_date": "2020-01-01",
                "supporter_tier": "gold",
            },
            team_id: {"team_name": f"Rebels {team_id}"},
        }

    monkeypatch.setattr(helperf.api, "ht_get_data", fake_get_data)
    monkeypatch.setattr(helperf.api, "ht_get_challengeable_teams", lambda xml: ["111"])
    monkeypatch.setattr(helperf.api, "ht_get_team", fake_team)

    result = helperf.get_challengeable_women_teams(
        "3242724", "home", ["111", "222"], "0", "all"
    )
    assert result == [("111", "Rebels 111")]
