import functools

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
	)

from . import api, db, decs, helperf



bp_a = Blueprint('auth', __name__, url_prefix='/auth')



@bp_a.route('/authorize', methods=('GET', 'POST'))
def authorize():
	if request.method == 'GET':
		g.authorize_url = api.oauth_get_url()

	elif request.method == 'POST':
		g.pin = request.form['pin']

		try:
			access_token_key, access_token_secret = api.oauth_get_access_token(g.pin)

		except:
			error = f"Pin {g.pin} was not accepted."
			flash(error)

		else:
			creds = f'{access_token_key} {access_token_secret}'

			session['encrypted_access_token'] = helperf.crypto_string(creds, "encrypt")


			return redirect(url_for('auth.login'))


	return render_template('auth/authorize.html')



@bp_a.route('/login', methods=('GET', 'POST'))
@decs.error_check
@decs.choose_team
def login():
	try:
		xml_response = api.ht_get_data('teamdetails', includeFlags='false')

	except:
		error = flash('Session initialization failed.')

	else:
		session['my_team'] = api.ht_get_team(xml_response)
		session['username'] = session['my_team']['user']['login_name']


		flash('login successful')


	return render_template('auth/login.html')



@bp_a.route('/logout')
@decs.error_check
def logout():
	g.username = session.get('username', None)
	error = None

	if g.username is None:
		error = 'Already logged out'

	if error is None:
		try:
			session.clear()
		except:
			error = f"Session logout failed"
	
		else:
			flash('logout successful')

	if error is not None:
		flash(error)


	return render_template('auth/logout.html')
