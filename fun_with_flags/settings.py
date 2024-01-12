""" View to customize settings for FwF. """

from datetime import datetime

from flask import Blueprint, current_app, flash, g, render_template, request

from . import decs

bp_s = Blueprint("settings", __name__, url_prefix="/settings")


@bp_s.route("/settings", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.error_check
def settings():
    g.db_settings = current_app.config["DB__SETTINGS_DICT"]
    something_changed = False

    # Bootstrap db-document if it doesn't exist
    if g.user_id not in g.couch:
        g.couch.save({"_id": g.user_id})

    # Instantiate clone of db-document
    g.my_document = g.couch[g.user_id]

    # Bootstrap settings-object if it doesn't exist
    if "settings" not in g.my_document:
        g.my_document["settings"] = {"meta": g.db_settings["meta"]}
        g.my_document["settings"].update(g.db_settings["defaults"])
        g.my_document["settings"]["meta"]["date_initialized"] = str(datetime.utcnow())
        something_changed = True

    # If settings-object exists, make sure schema is up-to-date
    if (
        g.my_document["settings"]["meta"]["schema_version"]
        < g.db_settings["meta"]["schema_version"]
    ):
        for _object in g.db_settings["objects"].items():
            if _object[0] not in g.my_document["settings"]:
                g.my_document["settings"][_object[0]] = {}

            for item_key in _object[1]["schema"]:
                if item_key not in g.my_document["settings"][_object[0]]:
                    g.my_document["settings"][_object[0]][item_key] = g.db_settings[
                        "defaults"
                    ][_object[0]][item_key]

        g.my_document["settings"]["meta"]["schema_version"] = g.db_settings["meta"][
            "schema_version"
        ]
        something_changed = True

    # Update settings-object with user changes
    if request.method == "POST":
        for item in request.form.items():
            _target_dict = item[0].split(".")[0]
            _key = item[0].split(".")[1]

            g.my_document["settings"][_target_dict][_key] = item[1]

        something_changed = True
        flash("Settings updated.")

    if something_changed:
        g.my_document["settings"]["meta"]["date_updated"] = str(datetime.utcnow())

    # Write changements on the settings-object to db
    g.couch[g.user_id] = g.my_document

    return render_template("settings/settings.html")
