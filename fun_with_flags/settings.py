"""View to customize settings for FwF."""

from datetime import datetime

from flask import Blueprint, current_app, flash, g, render_template, request

from . import db, decs

from flask_babel import gettext


bp_s = Blueprint("settings", __name__, url_prefix="/settings")


@bp_s.route("/settings", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_config_from_db
@decs.error_check
def settings():
    """ """
    _costs = current_app.config["COSTS"]
    g.costs_month_euro = float(_costs["costs_per_month"]) * float(
        _costs["factor_to_euro"]
    )
    g.costs_day_euro = float(g.costs_month_euro) / 30

    g.db_settings = current_app.config["DB__SETTINGS_DICT"]
    g.my_document = db.bootstrap_user_document(g.user_id, g.couch, g.db_settings)

    # Count g.total_payed_euro
    g.total_payed_euro = 0.0

    if "sessions" in g.my_document["unicorn"]["stripe"]:
        for pay_session in g.my_document["unicorn"]["stripe"]["sessions"]:
            if (
                "receipt_timestamp"
                in g.my_document["unicorn"]["stripe"]["sessions"][pay_session]
            ):
                _my_pay_session = g.my_document["unicorn"]["stripe"]["sessions"][
                    pay_session
                ]
                _amount = float(_my_pay_session["receipt_amount_received"])
                _factor = float(_my_pay_session["receipt_factor"])
                g.total_payed_euro += round(_amount * _factor, 2)

    # Update settings-object with user changes
    if request.method == "POST":
        for item in request.form.items():
            _target_dict = item[0].split(".")[0]
            _key = item[0].split(".")[1]

            g.my_document["settings"][_target_dict][_key] = item[1]

        g.my_document["settings"]["meta"]["date_updated"] = str(datetime.utcnow())

        flash(gettext("Settings updated."))

    # Write changements on the settings-object to db
    g.couch[g.user_id] = g.my_document

    return render_template("settings/settings.html")
