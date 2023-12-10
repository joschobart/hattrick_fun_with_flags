from flask import session

from ht_libs import do_challenge
from ht_libs import do_hattrick_request
from ht_libs import get_flags
from ht_libs import get_series
from ht_libs import get_teamdetails
from ht_libs import get_worlddetails



scope = 'manage_challenges'

session_status_url = 'https://chpp.hattrick.org/oauth/check_token.ashx'
api_url = 'https://chpp.hattrick.org/chppxml.ashx'

api_params =   {'teamdetails':			{	'file': 				'teamdetails', 
											'version': 				'3.6',
											'teamID':				'',
											'includeFlags': 		'',
								 		},
				'search_series':		{	'file': 				'search',
											'version':				'1.2',
											'searchType':			'3',
											'searchString':			'ii.1',					# e.g.: ii.1 for series II.1
											'searchLeagueID':		'',						# e.g.: 46 for switzerland
				 						},
				'worlddetails':			{	'file': 				'worlddetails',
											'version':				'1.9',
											'includeRegions':		'false',
											'leagueID':				'',						# e.g.: 46 for switzerland
				 						},
				'teams_in_series':		{	'file': 				'leaguedetails',
											'version':				'1.6',
											'leagueLevelUnitID':	'false',
				 						},
				'challengeable_teams':	{	'file': 				'challenges',
											'version':				'1.6',
											'actionType':			'challengeable',
											'teamId':				'',						# team to challenge
											'matchType':			'1',					# 0 = normal, 1 = cup-rules
											'matchPlace':			'',						# 0 = home, 1 = away
				 							'suggestedTeamIds':		'',						# CSV list of TeamIds
				 							},
				}



def oauth_get_url(scope=scope):
	session['request_token'], session['request_token_secret'], authorize_url = \
			do_hattrick_request.fetch_authorize_url(scope=scope)

	return authorize_url



def oauth_get_access_token(pin):
	session['access_token_key'], session['access_token_secret'] = do_hattrick_request.get_access_token(
				session['request_token'],
				session['request_token_secret'],
				pin,
				)

	session.pop('request_token', None)
	session.pop('request_token_secret', None)
    
	return



def oauth_open_session():
	ht_session = do_hattrick_request.open_auth_session(
					session['access_token_key'],
					session['access_token_secret'],
					)

	return ht_session



def ht_get_data(name, api_url=api_url, **kwargs):
	ht_session = oauth_open_session()

	params = api_params[name]

	params.update(kwargs)

	xml_data = ht_session.get(api_url, params=params)
	xml_data = str(xml_data.text).encode('latin1')\
									.decode('unicode_escape')\
									.encode('latin1')\
									.decode('utf8')

	print(params)

	return xml_data



def ht_get_team(xml_data):
	team_dict = get_teamdetails.get_teamdetails(xml_data)

	return team_dict



def ht_get_flags(teamdetails_xml):
	flags_dict = get_flags.get_my_flags(teamdetails_xml)

	return flags_dict



def get_missing_flags(teamdetails_xml):
	missing_flags_dict = get_flags.get_missing_flags(teamdetails_xml)

	return missing_flags_dict



def ht_get_worlddetails(worlddetails_xml):
	worlddetails_dict = get_worlddetails.get_my_worlddetails(worlddetails_xml)

	return worlddetails_dict



def ht_get_series(search_series_xml):
	series_dict = get_series.get_my_series(search_series_xml)

	return series_dict



def ht_get_teams_in_series(teams_in_series_xml):
	teams_dict = get_series.get_teams_in_series(teams_in_series_xml)

	return teams_dict



def ht_get_challengeable_teams(challengeable_xml):
	challengeable_teams_list = do_challenge.is_challengeable(challengeable_xml)

	return challengeable_teams_list
