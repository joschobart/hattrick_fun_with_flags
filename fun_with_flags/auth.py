import functools

from flask import (
	Blueprint, flash, g, redirect,
	render_template, request, session, url_for
	)

from . import api



bp_a = Blueprint('auth', __name__, url_prefix='/auth')



def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		username = session.get('username')

		if not username:

			return redirect(url_for('auth.authorize'))

		return view(**kwargs)

	return wrapped_view



@bp_a.route('/authorize', methods=('GET', 'POST'))
def authorize():
	if request.method == 'GET':
		g.authorize_url = api.oauth_get_url()

	elif request.method == 'POST':
		g.pin = request.form['pin']


		try:
			at = api.oauth_get_access_token(g.pin)

		except:
			error = f"Pin {g.pin} was not accepted."
			flash(error)

		else:
			return redirect(url_for("auth.login"))

	return render_template('auth/authorize.html')



@bp_a.route('/login', methods=('GET', 'POST'))
def login():
	access_token_key = session.get('access_token_key', None)
	access_token_secret = session.get('access_token_secret', None)

	error = None

	if access_token_key is None or access_token_secret is None:
		error = 'Can\'t process Data.'

	if error is None:
		try:
			xml_response = api.ht_get_data("teamdetails")

			session['my_team'] = api.ht_get_team(xml_response)

			session['username'] = session['my_team']['user']['login_name']

		except:
			error = f"Session initialization failed."

		else:
			flash('login successful')

	if error is not None:
		flash(error)

	return render_template('auth/login.html')



@bp_a.route('/logout')
def logout():
	access_token_key = session.get('access_token_key', None)
	access_token_secret = session.get('access_token_secret', None)
	g.username = session.get('username', None)
	error = None

	if access_token_key is None or access_token_secret is None:
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
