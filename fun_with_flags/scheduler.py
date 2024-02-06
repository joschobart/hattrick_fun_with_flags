""" View to customize schedules for FwF. """

from datetime import datetime

from flask import Blueprint, current_app, flash, g, render_template, request

from . import db, decs

bp_s = Blueprint("scheduler", __name__, url_prefix="/scheduler")


def sensor():
    """Function for regular job execution."""
    print("Scheduler is alive-er!")


@bp_s.route("/scheduler", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.error_check
def scheduler():
    pass

    return render_template("scheduler/scheduler.html")
