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
			xml = api.ht_get_data('teamdetails', teamID=team, includeFlags='false')
		
			_team =api.ht_get_team(xml)

			signup_year = _team['user']['signup_date'].split('-', 1)[0]
			actual_year = datetime.now().year

			
			if _team['user']['supporter_tier'] != 'none'\
				and int(actual_year) - int(signup_year) > 0:
				
				_team = (team, _team[team]['team_name'])
				g.challengeable.append(_team)

		print(g.challengeable)




# {'file': 'teamdetails', 'version': '3.6', 'teamID': '2065350', 'includeFlags': 'false'}
# {'user': {'user_id': '12104809', 'login_name': 'xxSandroxx', 'supporter_tier': 'platinum', 'signup_date': '2012-05-23 23:03:18'}, '857050': {'team_name': 'Mumak_2', 'team_short': 'Mumak_2', 'team_primary': 'True', 'team_country_id': '4', 'team_league_level_unit_id': '5932', 'team_league_level_unit_name': 'V.97', 'team_league_level_unit_level': '5', 'team_is_bot': 'False', 'team_in_cup': 'False'}, '2065350': {'team_name': 'Fc Livercool', 'team_short': 'Livercool', 'team_primary': 'False', 'team_country_id': '159', 'team_league_level_unit_id': '258573', 'team_league_level_unit_name': 'III.8', 'team_league_level_unit_level': '3', 'team_is_bot': 'False', 'team_in_cup': 'False'}}


# [{	'user': 	{	'user_id': '2495234', 
# 					'login_name': 'TITILASCIENCE', 
# 					'supporter_tier': 'platinum', 
# 					'signup_date': '2011-12-16 19:20:07'
# 					}, 
# 	'298619': 	{	'team_name': 'Personne', 
# 					'team_short': 'Personne', 
# 					'team_primary': 'True', 
# 					'team_country_id': '5', 
# 					'team_league_level_unit_id': '36394', 
# 					'team_league_level_unit_name': 'VI.406', 
# 					'team_league_level_unit_level': '6', 
# 					'team_is_bot': 'False', 
# 					'team_in_cup': 'False'
# 					},


	if request.method == 'POST':
		pass


	return render_template('flags/details.html')
