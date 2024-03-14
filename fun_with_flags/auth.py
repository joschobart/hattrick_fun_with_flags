""" FwF authentication views """


from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)

from . import api, decs, helperf

bp_a = Blueprint("auth", __name__, url_prefix="/auth")


@bp_a.route("/authorize", methods=("GET", "POST"))
def authorize():
    """ """
    if request.method == "GET":
        g.authorize_url = api.oauth_get_url()

    elif request.method == "POST":
        g.pin = request.form["pin"]

        try:
            access_token_key, access_token_secret = api.oauth_get_access_token(g.pin)

        except Exception as e:
            error = f"{e}: Pin {g.pin} was not accepted."
            flash(error)

        else:
            creds = f"{access_token_key} {access_token_secret}"

            session["encrypted_access_token"] = helperf.crypto_string(creds, "encrypt")

            return redirect(url_for("auth.login"))

    return render_template("auth/authorize.html")


@bp_a.route("/login", methods=("GET", "POST"))
@decs.choose_team
# @decs.error_check
def login():
    """ """
    try:
        token_status = api.ht_get_token_status(
            fernet_token=session["encrypted_access_token"]
        )

        xml_response = api.ht_get_data(
            "teamdetails", userID=token_status["user_id"][0], includeFlags="false"
        )
    except Exception as e:
        flash(f"Session initialization failed: {e}")

    else:
        session["my_team"] = api.ht_get_team(xml_response)
        session["username"] = session["my_team"]["user"]["login_name"]

        flash("login successful")

    return render_template("auth/login.html")


@bp_a.route("/logout")
@decs.error_check
def logout():
    """ """
    g.username = session.get("username", None)
    error = None

    if g.username is None:
        error = "Already logged out"

    if error is None:
        try:
            session.clear()
        except Exception as e:
            error = f"Session logout failed: {e}"

        else:
            flash("logout successful")

    if error is not None:
        flash(error)

    return render_template("auth/logout.html")
