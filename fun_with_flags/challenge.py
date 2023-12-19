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


	if g.challenges != []:

		if g.challenges['is_agreed'] == 'True':

			_now = datetime.now()
			match_time = g.challenges['match_time']
			match_time = datetime.strptime(match_time, '%Y-%m-%d %H:%M:%S')
			tdelta = match_time - _now
			tdelta = tdelta.total_seconds()
			g.tdelta_hours = round(tdelta / 3600, 1)

			session['my_team'][session['teamid']]['has_friendly'] = match_time

		
		print(session['my_team'][session['teamid']]['has_friendly'])


	else:
		message = f"No challenges to show"
		flash(message)





	return render_template('challenge/overview.html')



@bp_c.route('/challenge', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
@decs.error_check
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
			flash('Challenges booked!')
			return redirect(url_for("challenge.overview"))


	return render_template('challenge/challenge.html')
