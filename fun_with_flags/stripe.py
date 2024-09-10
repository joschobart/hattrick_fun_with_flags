"""View to handle payments with stripe for FwF."""

import binascii
import json
import os
from datetime import datetime

import stripe
from flask import (Blueprint, current_app, flash, g, jsonify, redirect,
                   render_template, request, session)
from flask_babel import gettext

from . import db, decs

bp_s = Blueprint("stripe", __name__, url_prefix="/stripe")


@bp_s.route("/checkout", methods=["POST"])
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.error_check
def checkout():
    """ """
    _session_token = binascii.hexlify(os.urandom(20)).decode()
    _url = request.args.get("url")
    _protocol = request.args.get("protocol")
    _domain = f"{_protocol}//{_url}/stripe"

    _price = os.environ["STRIPE_PRICE_ITEM"]
    # _price = os.environ["STRIPE_PRICE_ITEM_TEST"]

    stripe.api_key = os.environ["STRIPE_ENDPOINT_SECRET"]
    # stripe.api_key = os.environ["STRIPE_ENDPOINT_SECRET_TEST"]

    try:
        _stripe_user = stripe.Customer.search(query=f"name: '{session["username"]}'")
    except Exception as e:
        print(e)
        return

    if len(_stripe_user["data"]) == 0:
        try:
            _stripe_user = stripe.Customer.create(name=session["username"])
        except Exception as e:
            print(e)
            return
        else:
            _stripe_user = _stripe_user["id"]

    else:
        _stripe_user = _stripe_user["data"][0]["id"]

    try:
        _checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": _price,
                    "quantity": 1,
                },
            ],
            mode="payment",
            customer=_stripe_user,
            success_url=f"{_domain}/success?token={_session_token}",
            cancel_url=f"{_domain}/fail?token={_session_token}",
            automatic_tax={"enabled": True},
            customer_update={"address": "auto"},
        )

    except Exception as e:
        print(e)
        return

    _db_settings = current_app.config["DB__SETTINGS_DICT"]
    _my_document = db.bootstrap_user_document(g.user_id, g.couch, _db_settings)
    _my_document = db.init_stripe_session(
        g.user_id, g.couch, _stripe_user, _session_token, _checkout_session["id"]
    )
    # Write new session-object to db
    g.couch[g.user_id] = _my_document

    return redirect(_checkout_session.url, code=303)


@bp_s.route("/hook", methods=["POST"])
def hook():
    """ """
    stripe.api_key = os.environ["STRIPE_ENDPOINT_SECRET"]
    webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]
    # stripe.api_key = os.environ["STRIPE_ENDPOINT_SECRET_TEST"]
    # webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET_TEST"]

    event = None
    payload = request.data
    sig_header = request.headers.get("stripe-signature")

    try:
        event = json.loads(payload)

    except json.decoder.JSONDecodeError as e:
        print("  Webhook error while parsing basic request." + str(e))
        return jsonify(success=False)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except stripe.error.SignatureVerificationError as e:
        print("Webhook signature verification failed." + str(e))
        return jsonify(success=False)

    # Handle the succeeded event
    if event and event["type"] == "payment_intent.succeeded":
        _payment_intent = event["data"]["object"]

        _couch = db.get_db("fwf_cache")

        _object = {
            "id": _payment_intent["id"],
            "timestamp": str(datetime.utcnow()),
            "factor": "0.01",
            "amount_received": _payment_intent["amount_received"],
            "currency": _payment_intent["currency"],
        }

        try:
            _cache_document = db.bootstrap_generic_document(
                _payment_intent["customer"], _couch, _object
            )
        except TypeError:
            _payment_intent["customer"] = "1234_dummy"
            _cache_document = db.bootstrap_generic_document(
                _payment_intent["customer"], _couch, _object
            )

        # Write success-object to cache-db
        _couch[_payment_intent["customer"]] = _cache_document

    return jsonify(success=True)


@bp_s.route("/success", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_config_from_db
@decs.error_check
def success():
    """ """
    _session_token = request.args.get("token")

    _my_document = db.close_stripe_session(g.user_id, g.couch, _session_token)

    # Write success-object to cache-db
    g.couch[g.user_id] = _my_document

    flash(gettext("Payment accepted. You're a FwF Unicorn now!"))

    return render_template("stripe/hook.html")


@bp_s.route("/fail", methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
@decs.use_db
@decs.set_config_from_db
@decs.error_check
def fail():
    """ """
    _session_token = request.args.get("token")

    _my_document = db.close_stripe_session(g.user_id, g.couch, _session_token)

    # Write success-object to cache-db
    g.couch[g.user_id] = _my_document

    flash(gettext("No payment received."))

    return render_template("stripe/hook.html")
