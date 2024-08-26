"""FwF Flask-Factory"""

import atexit
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, send_from_directory, session
from flask_babel import Babel
from werkzeug.middleware.proxy_fix import ProxyFix

from . import (achievements, auth, challenge, decs, flags, scheduler, settings,
               stripe)


def create_app(test_config=None):
    """Creates and configures the app.

    :param test_config: Default value = None)

    """

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ["FLASK_SECRET"],
    )

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # setup scheduler
    sched = BackgroundScheduler(daemon=True)
    # regular job for challenging friendlies
    sched.add_job(scheduler.sensor, "cron", day_of_week="thu", hour=8, minute=15)
    # regular job for adding matches to user-db
    sched.add_job(scheduler.sensor, "cron", day_of_week="tue", hour=1, minute=25)
    #  v--- testing ---v
    # sched.add_job(scheduler.sensor, "cron", day_of_week="mon-sun", hour=21, minute=40)
    sched.start()
    atexit.register(lambda: sched.shutdown(wait=False))

    # setup logger for scheduler
    logging.basicConfig()
    logging.getLogger("apscheduler").setLevel(logging.INFO)

    # Babel l10n
    def get_locale():
        supported_langs = ["en"] + os.listdir(f"{app.root_path}/translations")

        if not session.get("lang", None):
            if request.accept_languages.best_match(supported_langs):
                session["lang"] = request.accept_languages.best_match(supported_langs)

        if request.args.get("lang"):
            if request.args.get("lang") in supported_langs:
                session["lang"] = request.args.get("lang")

        return session.get("lang", "en")

    babel = Babel()
    babel.init_app(app, locale_selector=get_locale)

    # entry-point
    @app.route("/", methods=("GET", "POST"))
    @decs.choose_team
    @decs.set_config_from_db
    def index():
        """index.html view."""

        return render_template("index.html")

    @app.route("/favicon.ico")
    def fav():
        """Hack to make favicon available."""

        return send_from_directory(app.static_folder, "favicon.ico")

    app.register_blueprint(achievements.bp_a)
    app.register_blueprint(auth.bp_a)
    app.register_blueprint(challenge.bp_c)
    app.register_blueprint(flags.bp_f)
    app.register_blueprint(settings.bp_s)
    app.register_blueprint(stripe.bp_s)

    return app
