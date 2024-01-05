import functools

from flask import flash, g, redirect, request, session, url_for

from . import db, helperf


def error_check(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        error = None

        try:
            view(**kwargs)

        except:
            error = f"Something went wrong on page '{view.__name__}'. \
                                Please try again or report an error to joschobart on hattrick.org."

        if error is not None:
            flash(error)

            return redirect(url_for('index'))


        return view(**kwargs)

    return wrapped_view



def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        username = session.get('username')

        if not username:
            return redirect(url_for('auth.authorize'))


        return view(**kwargs)

    return wrapped_view



def choose_team(view):
    @functools.wraps(view)

    def wrapped_view(**kwargs):
        if 'username' in session:
            helperf.get_my_teams()

            if request.method == 'POST' and 'teams' in request.form:
                session['teamid'] = request.form['teams']

                return redirect(url_for('flags.overview'))


        return view(**kwargs)

    return wrapped_view



def use_db(view):
    @functools.wraps(view)

    def wrapped_view(**kwargs):
        if 'my_team' in session:
            g.db_instance = db.get_db()
            g.db_doc_id = session['my_team']['user']['user_id']


        return view(**kwargs)

    return wrapped_view
