from flask import (
    Blueprint, flash, g, redirect,
    render_template, request, session, url_for
	)

from . import auth
from . import api



bp_f = Blueprint('flags', __name__, url_prefix='/flags')



@bp_f.route('/overview', methods=('GET', 'POST'))
@auth.login_required
def overview():
	g.teams = list()

	for x in list(session['my_team']):
		if x != 'user':
			team = (x, session['my_team'][x]['team_name'], session['my_team'][x]['team_primary'])
			g.teams.append(team)

	# first sort after 'team_primary', then team_id
	g.teams = sorted(g.teams, key=lambda x: (x[2], x[0]), reverse=True)


	base_url = 'https://www.hattrick.org/Img/flags/'
	url_end_i = '_inactive.png'
	url_end = '.png'


	xml_data = api.ht_get_data("teamdetails")
	my_flags = api.ht_get_flags(xml_data)


	get_my_missing_flags = api.get_missing_flags(xml_data)
	print(get_my_missing_flags)

	g.l_home = []
	g.l_away = []

	
	for ha in ['flags_home', 'flags_away']:
		for x in range(len(my_flags[g.teams[0][0]][ha])):
			w = my_flags[g.teams[0][0]][ha][x][1]
			w = w.replace('ô', 'o')
			w = w.replace('ã', 'a')

			if ha == 'flags_home':
				g.l_home.append((w, (base_url + \
						my_flags[g.teams[0][0]][ha][x][0] + \
						url_end)))

			else:
				g.l_away.append((w, (base_url + \
						my_flags[g.teams[0][0]][ha][x][0] + \
						url_end)))				

	g.l_home = sorted(g.l_home, key=lambda x: x[0])
	g.l_away = sorted(g.l_away, key=lambda x: x[0])


	return render_template('flags/overview.html')

# 22 / reihe
# https://www.hattrick.org/Img/flags/33_inactive.png
# https://www.hattrick.org/Img/flags/33.png