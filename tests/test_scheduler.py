"""Scheduler opponent search: men's tree vs. women's index, and the home/away bug."""

import pytest

from fun_with_flags import scheduler


def test_men_schedule_passes_home_not_zero(monkeypatch):
    seen = {}
    monkeypatch.setattr(scheduler.helperf, "get_series_list", lambda *a, **k: ["s1"])

    def fake_men(team_id, place, series, *a, **k):
        seen.update(place=place, series=series)
        return []

    monkeypatch.setattr(scheduler.helperf, "get_challengeable_teams_list", fake_men)
    scheduler.find_opponents("628463", "1", "46", "home", "2", "0", "all", "tok")
    assert seen == {"place": "home", "series": ["s1"]}  # was "0" → treated as away 🐛


def test_women_schedule_uses_index_never_men_tree(monkeypatch):
    seen = {}
    monkeypatch.setattr(scheduler.women_index, "index_ready", lambda: True)
    monkeypatch.setattr(
        scheduler.women_index, "candidates",
        lambda flag, exclude=(): ["111"] if flag == "3" else [],
    )

    def fake_women(team_id, place, cands, *a, **k):
        seen.update(place=place, cands=cands)
        return [("111", "Rebels")]

    monkeypatch.setattr(scheduler.helperf, "get_challengeable_women_teams", fake_women)
    monkeypatch.setattr(
        scheduler.helperf, "get_series_list",
        lambda *a, **k: pytest.fail("women's team searched the men's tree!"),
    )

    assert scheduler.find_opponents("3242724", "2", "3", "home", "2", "0", "all", "tok") == [
        ("111", "Rebels")
    ]
    assert seen == {"place": "home", "cands": ["111"]}


def test_women_schedule_without_index_finds_nothing(monkeypatch):
    monkeypatch.setattr(scheduler.women_index, "index_ready", lambda: False)
    assert scheduler.find_opponents("3242724", "2", "3", "home", "2", "0", "all", "tok") == []
