from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from . import api, db, decs, helperf

bp_s = Blueprint('settings', __name__, url_prefix='/settings')



@bp_s.route('/overview', methods=('GET', 'POST'))
@decs.login_required
@decs.choose_team
@decs.use_db
#@decs.error_check
def overview():
    try:
        g.couch[g.user_id]
    except Exception as e:
        g.couch.save({'_id': g.user_id})

    my_document = g.couch[g.user_id]


    
    print(my_document)

    return render_template('settings/overview.html')
