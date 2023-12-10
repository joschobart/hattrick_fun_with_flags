from datetime import datetime

from flask import (Blueprint,
	g, render_template, request,)

from . import api
from . import decs
from . import helperf



bp_f = Blueprint('flags', __name__, url_prefix='/flags')



@bp_f.route('/overview', methods=('GET', 'POST'))
@decs.login_required
@decs.error_check
def overview():
	helperf.get_my_teams()

	if request.method == 'POST':
		g.teamid = request.form['teams']

		g.l_home, g.l_away = helperf.compose_flag_matrix(g.teamid)

		g.l_home = sorted(g.l_home, key=lambda x: x[1])
		g.l_away = sorted(g.l_away, key=lambda x: x[1])


	return render_template('flags/overview.html')



@bp_f.route('/details', methods=('GET', 'POST'))
@decs.login_required
#@decs.error_check
def details():
	g.challengeable = []

	g.flagid = request.args.get('flagid')
	g.teamid = request.args.get('teamid')
	g.place = request.args.get('place')

	g.l_home, g.l_away = helperf.compose_flag_matrix(g.teamid)

	helperf.get_my_teams()


	for item in g.teams:
		if int(item[0]) == int(g.teamid):
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


	if g.missing_flag:
		sl = helperf.get_series_list(g.flagid)

		ctl = helperf.get_challengeable_teams_list(g.teamid, g.place, sl)

		for team in ctl:
			_xml = api.ht_get_data('teamdetails', teamID=team, includeFlags='false')
			_team =api.ht_get_team(_xml)

			signup_year = _team['user']['signup_date'].split('-', 1)[0]
			actual_year = datetime.now().year
			
			if _team['user']['supporter_tier'] != 'none' and\
			int(actual_year) - int(signup_year) > 0:
				
				_team = (team, _team[team]['team_name'])
				g.challengeable.append(_team)


	if request.method == 'POST':
		pass					# not yet implemented


	return render_template('flags/details.html')
