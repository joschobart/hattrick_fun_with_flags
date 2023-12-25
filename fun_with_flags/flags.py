from datetime import datetime

from flask import (Blueprint,
	g, render_template, request,session,)

from . import api
from . import decs
from . import helperf
from . import db



bp_f = Blueprint('flags', __name__, url_prefix='/flags')


@bp_f.route('/overview', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
@decs.error_check
def overview():
	g.l_home, g.l_away, g.nr_flags_home, g.nr_flags_away =\
				helperf.compose_flag_matrix(session['teamid'])


	g.l_home = sorted(g.l_home, key=lambda x: x[1])
	g.l_away = sorted(g.l_away, key=lambda x: x[1])


	return render_template('flags/overview.html')



@bp_f.route('/details', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
@decs.error_check
def details():
	g.challengeable = []

	g.flagid = request.args.get('flagid')
	g.place = request.args.get('place')

	g.l_home, g.l_away, *_ = helperf.compose_flag_matrix(session['teamid'])


	gmc = helperf.get_my_challenges()	
	g.bookable = gmc[-1]


	for item in session['teams']:
		if int(item[0]) == int(session['teamid']):
			g.team = item[1]
			break


	if g.place == 'home':
		func = g.l_home[:]
	else:
		func = g.l_away[:]


	for item in func:
		if int(item[0]) == int(g.flagid):
			g.nation  = item[1]
			g.flagurl = item[2]

			if 'inactive' in g.flagurl:
				g.missing_flag = True
			else:
				g.missing_flag = False
			break


	if request.method == 'POST':
		if g.missing_flag:
			sl = helperf.get_series_list(g.flagid)

			ctl = helperf.get_challengeable_teams_list(session['teamid'], g.place, sl)


			for team in ctl:
				_xml = api.ht_get_data('teamdetails', teamID=team, includeFlags='false')
				_team =api.ht_get_team(_xml)

				signup_year = _team['user']['signup_date'].split('-', 1)[0]
				actual_year = datetime.now().year
			
				if _team['user']['supporter_tier'] != 'none' and\
				int(actual_year) - int(signup_year) > 0:
				
					_team = (team, _team[team]['team_name'])
					g.challengeable.append(_team)


		session['challengeable'] = g.challengeable


	return render_template('flags/details.html')
