# -*- coding: utf-8 -*-

import logging
import os
import sys

from flask import Flask
from flask_mail import Mail
from flask_oauthlib.client import OAuth

from engineering_diplomats.controllers import Mailer, MongoConnector
from engineering_diplomats.routes import apply_routes
from engineering_diplomats.settings import microsoft_oauth_config, app_config_kwargs
from engineering_diplomats.views.views import SiteHandler


# Logging setup
ld = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(ld)
fh = logging.FileHandler("./logs/main.log")
fh.setLevel(ld)
ch = logging.StreamHandler()
ch.setLevel(ld)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)


def init_app() -> Flask:
	"""Initialize the application"""
	app = Flask(
		"engineeringdiplomats[dot]org",
		static_folder=os.environ.get("STATIC_FOLDER"),
		template_folder=os.environ.get("TEMPLATE_FOLDER"),
	)
	app.url_map.strict_slashes = False
	app.config.update(**app_config_kwargs)
	app.logger = logger

	oauth = OAuth(app)
	db = MongoConnector(app)
	mailer = Mailer(Mail(app))
	
	microsoft = oauth.remote_app("microsoft", **microsoft_oauth_config)
	site_handler = SiteHandler(db, microsoft, mailer)
	site_handler.get_token = microsoft.tokengetter(site_handler.get_token)
	
	app = apply_routes(app, site_handler)

	return app


if __name__ == "__main__": # pragma: no cover
	init_app().run(host="0.0.0.0", port=8080, debug=True)
