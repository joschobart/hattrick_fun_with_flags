import os

import couchdb
from flask import g


def get_db():
    if 'couch' not in g:
        couch = couchdb.Server(os.environ['COUCHDB_CONNECTION_STRING'])

        try:
            g.couch = couch['fwf_db'] # existing

        except Exception as e:
            print(f"CouchDB server not available: {e}")


    return g.couch
