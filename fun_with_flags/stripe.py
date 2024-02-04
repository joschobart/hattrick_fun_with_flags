""" View to handle payments with stripe for FwF. """

import json
import os
import uuid

import stripe
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, session)

from . import decs

bp_s = Blueprint("stripe", __name__, url_prefix="/stripe")


@bp_s.route('/checkout', methods=["POST"])
@decs.login_required
@decs.choose_team
#@decs.error_check
def checkout():
    _uuid = uuid.uuid4()
    _url = request.args.get("url")
    _protocol = request.args.get("protocol")
    _domain = f"{_protocol}//{_url}/stripe"

    stripe.api_key = os.environ["STRIPE_TOKEN"]
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1OfnlcGBvDAda5rUfbE5PrRl',
                    'quantity': 1,
                },
            ],
            mode = 'payment',
            success_url = f"{_domain}/success?uuid={_uuid}",
            cancel_url = f"{_domain}/fail?uuid={_uuid}",
            automatic_tax={'enabled': True},
        )

    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@bp_s.route('/hook', methods=["POST"])
def hook():
    stripe.api_key = os.environ["STRIPE_TOKEN"]
    endpoint_secret = os.environ["STRIPE_ENDPOINT_SECRET"]

    event = None
    payload = request.data
    sig_header = request.headers.get('stripe-signature')

    try:
        event = json.loads(payload)

    except json.decoder.JSONDecodeError as e:
        print('  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)
        
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError as e:
        print('Webhook signature verification failed.' + str(e))
        return jsonify(success=False)

    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        session["unicorn"] = (payment_intent["created"], payment_intent['amount'])

    return jsonify(success=True)


@bp_s.route('/success', methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
#@decs.error_check
def success():
    session["unicorn"] = True
    flash("Payment accepted. You're a FwF Unicorn now!")

    return render_template("stripe/hook.html")


@bp_s.route('/fail', methods=("GET", "POST"))
@decs.login_required
@decs.choose_team
#@decs.error_check
def fail():
    _uuid = request.args.get("uuid")
    print(_uuid)
    session["unicorn"] = False
    flash("No payment received.")

    return render_template("stripe/hook.html")
