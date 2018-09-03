# -*- coding: utf-8 -*-

import logging
import os
import sys

from flask import Flask
from flask_oauthlib.client import OAuth

from engineeringdiplomats.models import MongoConnector
from engineeringdiplomats.routes import apply_routes
from engineeringdiplomats.views import SiteHandler
from engineeringdiplomats.settings import microsoft_oauth_config

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

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")
RECAPTCHA_PARAMETERS = {"hl": "en", "render": "explicit"}
RECAPTCHA_DATA_ATTRS = {"theme": "dark"}

def init_app() -> Flask:
	"""Initialize the application"""
	app = Flask(
		"engineeringdiplomats[dot]org",
		static_folder=os.environ["STATIC_FOLDER"],
		template_folder=os.environ["TEMPLATE_FOLDER"],
	)
	app.url_map.strict_slashes = False
	app.config.from_object(__name__)
	app.logger = logger

	oauth = OAuth(app)
	db = MongoConnector(app)

	microsoft = oauth.remote_app("microsoft", **microsoft_oauth_config)
	site_handler = SiteHandler(db, microsoft)
	site_handler.get_token = microsoft.tokengetter(site_handler.get_token)
	
	app = apply_routes(app, site_handler)
	app.secret_key = os.environ["SECRET_KEY"]

	return app


if __name__ == "__main__": # pragma: no cover
	init_app().run(host="0.0.0.0", port=8080, debug=True)
