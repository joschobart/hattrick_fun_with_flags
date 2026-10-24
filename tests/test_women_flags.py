"""Women's teams map to the right flag, men's teams don't change."""

from pathlib import Path

import pytest
from ht_libs import get_teamdetails

from fun_with_flags import api

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def teams(monkeypatch):
    world = (FIX / "worlddetails_v2.0_trimmed.xml").read_bytes()
    monkeypatch.setattr(api, "ht_get_data", lambda *a, **k: world)
    api._FLAG_MAP.update(data=None, ts=0.0)
    return get_teamdetails.get_teamdetails((FIX / "teamdetails_v3.9_two_teams.xml").read_bytes())


def test_men_team_keeps_league_id(teams):
    assert api.flag_id_of_team(teams["628463"]) == "46"


def test_women_team_gets_swiss_flag(teams):
    assert api.flag_id_of_team(teams["3242724"]) == "46"  # CountryID 40 → 🇨🇭


def test_czech_women_team_never_gets_swiss_flag(teams):
    czech = dict(teams["3242724"], team_real_country_id="46")
    assert api.flag_id_of_team(czech) == "52"  # 🇨🇿≠🇨🇭


def test_old_session_women_team_detected_by_league_3000():
    # session built before the deploy (teamdetails 3.6): no team_gender_id
    old = {"team_country_id": "3000"}
    assert api.is_women_team(old)


def test_old_session_men_team_stays_men():
    assert not api.is_women_team({"team_country_id": "46"})
    assert api.flag_id_of_team({"team_country_id": "46"}) == "46"
