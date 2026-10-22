from pathlib import Path

from fun_with_flags import api


def test_worlddetails_real_response_parses():
    xml = (Path(__file__).parent / "fixtures" / "worlddetails.xml").read_bytes()
    assert api.ht_get_worlddetails(xml)["season_round"] == "14"
