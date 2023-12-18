from datetime import datetime

from flask import (Blueprint,
	g, render_template, request, session, redirect, flash)

from . import api
from . import decs
from . import helperf



bp_c = Blueprint('challenge', __name__, url_prefix='/challenge')



@bp_c.route('/overview', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
#@decs.error_check
def overview():
	g.challenges = []
	teamid = session.get('teamid', None)

	_xml = api.ht_get_data('get_challenges', teamId=teamid)


	try:
		g.challenges = api.ht_get_challenges(_xml)

	except:
		error = f"Getting challenges was unsuccessful."
		
		flash(error)


	return render_template('challenge/overview.html')



@bp_c.route('/challenge', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
#@decs.error_check
def challenge():
	if request.method == 'POST':
		g.challengeable = list(zip(*session.get('challengeable', None)))[0]
		g.teamid = session.get('teamid', None)

		session.pop('challengeable', None)


		try:
			challenge = api.ht_do_challenge(g.teamid, g.challengeable)

		except:
			error = f"Do challenge was unsuccessful."
			flash(error)

		else:
			return redirect(url_for("challenge.overview"))


	return render_template('challenge/challenge.html')
