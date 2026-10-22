from fun_with_flags import api

def test_api_params_are_not_mutated(monkeypatch):
    calls = []

    class FakeSession:
        def get(self, url, params):
            calls.append(dict(params))
            return type("R", (), {"text": "<HattrickData/>"})()
        def close(self):
            pass

    monkeypatch.setattr(api, "oauth_open_session", lambda token="": FakeSession())
    api.ht_get_data("teamdetails", fernet_token="x", userID="111")
    api.ht_get_data("teamdetails", fernet_token="x", teamID="222")

    assert calls[1]["userID"] == ""            # no leftover from the first call
    assert api.API_PARAMS["teamdetails"]["userID"] == ""
