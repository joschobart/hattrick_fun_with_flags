"""Smoke tests: the app starts, renders, and the login building blocks work."""

import pytest
from ht_libs import request_token_status

from fun_with_flags import create_app, helperf


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def test_index_renders_for_anonymous_user(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Fun with Flags" in response.data


def test_fernet_roundtrip():
    creds = "access-key access-secret"
    encrypted = helperf.crypto_string(creds, "encrypt")
    assert helperf.crypto_string(encrypted, "decrypt") == creds


def test_ht_libs_contract_used_by_login():
    # auth.login() does token_status["user_id"][0]
    xml = "<HattrickData><UserID>42</UserID></HattrickData>"
    assert request_token_status.request_token_status(xml)["user_id"][0] == "42"

def test_all_templates_compile():
    app = create_app()
    env = app.jinja_env
    for name in env.list_templates(extensions=["html"]):
        env.get_template(name)   # raises TemplateSyntaxError on broken templates

def test_worldmap_renders():
    flags = {"123": {"flags_home": [("46", "Switzerland", "CH", "EU")], "flags_away": []}}
    assert helperf.render_worldmap(flags, "123").startswith("data:image/svg+xml")
