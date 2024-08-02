"""FwF authentication views"""

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_babel import gettext

from . import api, decs, helperf

bp_a = Blueprint("auth", __name__, url_prefix="/auth")


@bp_a.route("/authorize", methods=("GET", "POST"))
def authorize():
    """ """
    _protocol = request.args.get("protocol")
    _url = request.args.get("url")

    if request.method == "GET":
        if _protocol and _url:
            g.authorize_url = api.oauth_get_url(
                oauth_url=f"{_protocol}//{_url}/auth/callback"
            )
            g.oob = False
        else:
            g.authorize_url = api.oauth_get_url()
            g.oob = True

    if request.method == "POST":
        g.pin = request.form["pin"]
        try:
            access_token_key, access_token_secret = api.oauth_get_access_token(g.pin)
        except Exception as e:
            error = gettext("{e}: Pin {pin} was not accepted.".format(e=e, pin=g.pin))
            flash(error)
        else:
            creds = f"{access_token_key} {access_token_secret}"
            session["encrypted_access_token"] = helperf.crypto_string(creds, "encrypt")
            return redirect(url_for("auth.login"))

    return render_template("auth/authorize.html")


@bp_a.route("/callback")
def callback():
    """ """
    g.pin = request.args.get("oauth_verifier")

    try:
        access_token_key, access_token_secret = api.oauth_get_access_token(g.pin)

    except Exception as e:
        error = gettext("{e}: Pin {pin} was not accepted.".format(e=e, pin=g.pin))

        flash(error)

    else:
        creds = f"{access_token_key} {access_token_secret}"
        session["encrypted_access_token"] = helperf.crypto_string(creds, "encrypt")
        return redirect(url_for("auth.login"))

    return render_template("auth/authorize.html")


@bp_a.route("/login", methods=("GET", "POST"))
@decs.choose_team
@decs.error_check
def login():
    """ """
    try:
        token_status = api.ht_get_token_status(
            fernet_token=session["encrypted_access_token"]
        )

        xml_response = api.ht_get_data(
            "teamdetails",
            teamID="",
            userID=token_status["user_id"][0],
            includeFlags="false",
        )
    except Exception as e:
        flash(gettext("Session initialization failed: {e}".format(e=e)))

    else:
        session["my_team"] = api.ht_get_team(xml_response)
        session["username"] = session["my_team"]["user"]["login_name"]

        flash(gettext("login successful"))

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
            error = gettext("Session logout failed: {e}".format(e=e))

        else:
            flash(gettext("logout successful"))

    if error is not None:
        flash(error)

    return render_template("auth/logout.html")
