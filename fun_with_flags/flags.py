from flask import (
    Blueprint, g, render_template, 
    request, session,
	)


from . import auth
from . import api



bp_f = Blueprint('flags', __name__, url_prefix='/flags')



def compose_flag_matrix(teamid, l_home, l_away):
	xml_data = api.ht_get_data("teamdetails")

	my_flags = api.ht_get_flags(xml_data)
	my_missing_flags = api.get_missing_flags(xml_data)

	base_url = 'https://www.hattrick.org/Img/flags/'
	url_end_i = '_inactive.png'
	url_end = '.png'


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
@auth.login_required
def overview():
	g.teams = list()

	for x in list(session['my_team']):
		if x != 'user':
			team = (x, session['my_team'][x]['team_name'], session['my_team'][x]['team_primary'])
			g.teams.append(team)

	# first sort after 'team_primary', then team_id
	g.teams = sorted(g.teams, key=lambda x: (x[2], x[0]), reverse=True)


	if request.method == 'POST':
		g.teamid = request.form['teams']
		g.l_home = []
		g.l_away = []

		compose_flag_matrix(g.teamid, g.l_home, g.l_away)

		g.l_home = sorted(g.l_home, key=lambda x: x[0])
		g.l_away = sorted(g.l_away, key=lambda x: x[0])


	return render_template('flags/overview.html')



@bp_f.route('/details', methods=('GET', 'POST'))
@auth.login_required
def details():
	flag_id = request.args.get('flagid')
	print(flag_id)


	return render_template('flags/details.html')
