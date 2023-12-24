import os

from pymongo import MongoClient

from pymongo.errors import ConnectionFailure

from flask import g



def get_db():
	if 'db' not in g:
		db_client = MongoClient(os.environ['MONGODB_CONNECTION_STRING'])

		try:
			db_client.admin.command('ping')

		except ConnectionFailure:
			print("MongoDB server not available")

			g.db = db_client['ht_fwf']


	return g.db



def close_db(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()
