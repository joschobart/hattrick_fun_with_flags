""" View to customize settings for FwF. """

from datetime import datetime

from flask import Blueprint, current_app, flash, g, render_template, request

from . import db, decs

bp_s = Blueprint("settings", __name__, url_prefix="/settings")


@bp_s.route("/settings", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
# @decs.error_check
def settings():
    g.db_settings = current_app.config["DB__SETTINGS_DICT"]
    g.my_document = db.bootstrap_document(g.user_id, g.couch, g.db_settings)

    # Update settings-object with user changes
    if request.method == "POST":
        for item in request.form.items():
            _target_dict = item[0].split(".")[0]
            _key = item[0].split(".")[1]

            g.my_document["settings"][_target_dict][_key] = item[1]

        g.my_document["settings"]["meta"]["date_updated"] = str(datetime.utcnow())

        flash("Settings updated.")

    # Write changements on the settings-object to db
    g.couch[g.user_id] = g.my_document

    return render_template("settings/settings.html")
