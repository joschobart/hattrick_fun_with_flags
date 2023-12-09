from flask import (
    Blueprint, g, render_template, 
    request, session,
	)

from . import auth
from . import api
from . import decs



bp_f = Blueprint('flags', __name__, url_prefix='/flags')



def get_my_teams():
	g.teams = []


	for x in list(session['my_team']):
		if x != 'user':
			team = (x, session['my_team'][x]['team_name'], session['my_team'][x]['team_primary'])
			g.teams.append(team)

	# first sort after 'team_primary', then team_id
	g.teams = sorted(g.teams, key=lambda x: (x[2], x[0]), reverse=True)


	return g.teams



def compose_flag_matrix(teamid):
	xml_data = api.ht_get_data("teamdetails")

	my_flags = api.ht_get_flags(xml_data)
	my_missing_flags = api.get_missing_flags(xml_data)

	base_url = 'https://www.hattrick.org/Img/flags/'
	url_end_i = '_inactive.png'
	url_end = '.png'

	g.l_home = []
	g.l_away = []
	

	for m in (my_flags, my_missing_flags):
		for ha in m[teamid].keys():
			for flag in range(len(m[teamid][ha])):
				i = m[teamid][ha][flag][0]
				w = m[teamid][ha][flag][1]
				w = w.replace('ô', 'o')
				w = w.replace('ã', 'a')

				if ha == 'missing_home':
					g.l_home.append((i, w, (base_url + \
							m[g.teamid][ha][flag][0] + \
							url_end_i)))

				elif ha == 'flags_home':
					g.l_home.append((i, w, (base_url + \
							m[g.teamid][ha][flag][0] + \
							url_end)))

				elif ha == 'missing_away':
					g.l_away.append((i, w, (base_url + \
							m[g.teamid][ha][flag][0] + \
							url_end_i)))

				else:
					g.l_away.append((i, w, (base_url + \
							m[g.teamid][ha][flag][0] + \
							url_end)))


	return g.l_home, g.l_away



@bp_f.route('/overview', methods=('GET', 'POST'))
@decs.login_required
@decs.error_check
def overview():
	get_my_teams()

	if request.method == 'POST':
		g.teamid = request.form['teams']

		compose_flag_matrix(g.teamid)

		g.l_home = sorted(g.l_home, key=lambda x: x[1])
		g.l_away = sorted(g.l_away, key=lambda x: x[1])


	return render_template('flags/overview.html')



@bp_f.route('/details', methods=('GET', 'POST'))
@decs.login_required
#@decs.error_check
def details():
	g.flagid = request.args.get('flagid')
	g.teamid = request.args.get('teamid')
	g.place = request.args.get('place')
	

	compose_flag_matrix(g.teamid)
	get_my_teams()

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
				g.challengeable = True
			
			break

	result =	api.ht_get_data('search_series', searchString='iii.1', searchLeagueID='46')
	print(result)


	if request.method == 'POST':
		pass

	return render_template('flags/details.html')



