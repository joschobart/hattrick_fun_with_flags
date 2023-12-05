from flask import session

from ht_libs import do_hattrick_request
from ht_libs import get_teamdetails
from ht_libs import get_flags



scope = 'manage_challenges'

session_status_url = 'https://chpp.hattrick.org/oauth/check_token.ashx'
api_url = 'https://chpp.hattrick.org/chppxml.ashx'

api_params =	{'teamdetails': {	'file': 'teamdetails', 
									'version': '3.6',
									'includeFlags': 'true',
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


def ht_get_data(name, *args, api_url=api_url, **kwargs):
	ht_session = oauth_open_session()

	params = api_params[name]

	xml_data = ht_session.get(api_url, params=params)
	xml_data = str(xml_data.text).encode('latin1')\
									.decode('unicode_escape')\
									.encode('latin1')\
									.decode('utf8')

	return xml_data


def ht_get_team(xml_data):
	team_dict = get_teamdetails.get_my_teamdetails(xml_data)

	return team_dict


def ht_get_flags(teamdetails_xml):
	flags_dict = get_flags.get_my_flags(teamdetails_xml)

	return flags_dict


def get_missing_flags(teamdetails_xml):
	missing_flags_dict = get_flags.get_missing_flags(teamdetails_xml)

	return missing_flags_dict