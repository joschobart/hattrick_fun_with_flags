from datetime import datetime

from flask import (Blueprint,
	g, render_template, request, session, redirect, url_for, flash)

from . import api
from . import decs
from . import helperf



bp_c = Blueprint('challenge', __name__, url_prefix='/challenge')



@bp_c.route('/overview', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
#@decs.error_check
def overview():
	g.challenges, now, match_time, tdelta, g.tdelta_hours, bookable = helperf.get_my_challenges()
	teamid = session.get('teamid', None)


	if g.challenges['challenges'] != []:
		if g.challenges['challenges'][0]['is_agreed'] == 'True':
			if now.weekday() in range(0, 3) and g.tdelta_hours > 100:
				message = f"Match is running.\
							Come back Thursday after 7 o'clock UTC to book a new match."

				session['my_team'][session['teamid']]['has_friendly'] = None
				g.challenges.clear()

			else:
				message = f"Match booked!"

				session['my_team'][session['teamid']]['has_friendly'] = match_time


		else:
			message = f"Teams are challenged but not agreed yet."


	else:
		message = f"No challenges to show"

		session['my_team'][session['teamid']]['has_friendly'] = None


	flash(message)


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
			flash('Challenges booked!')
			return redirect(url_for("challenge.overview"))


	return render_template('challenge/challenge.html')
