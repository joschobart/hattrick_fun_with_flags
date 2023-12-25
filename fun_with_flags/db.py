import couchdb
import os

from flask import g



def get_db():
	if 'couch' not in g:
		couch = couchdb.Server(os.environ['COUCHDB_CONNECTION_STRING'])

		try:
			g.couch = couch['fwf_db'] # existing

		except:
			print("CouchDB server not available")


	return g.couch
