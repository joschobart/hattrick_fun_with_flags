"""Dummy environment so the app can be imported and created in tests."""

import os

from cryptography.fernet import Fernet

os.environ.setdefault("HATTRICK_OAUTH_CONSUMER_KEY", "dummy-key")
os.environ.setdefault("HATTRICK_OAUTH_CONSUMER_SECRET", "dummy-secret")
os.environ.setdefault("FLASK_SECRET", "dummy-flask-secret")
os.environ.setdefault("FERNET_SECRET", Fernet.generate_key().decode())
os.environ.setdefault("COUCHDB_CONNECTION_STRING", "http://localhost:5984/")
