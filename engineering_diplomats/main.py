# -*- coding: utf-8 -*-

import os
import sys

import logme

from flask import Flask
from flask_mail import Mail
from flask_oauthlib.client import OAuth

from opencensus.trace.exporters import stackdriver_exporter
from opencensus.trace.ext.flask.flask_middleware import FlaskMiddleware as Tracing
from opencensus.trace.exporters.transports.background_thread \
    import BackgroundThreadTransport

from engineering_diplomats.controllers import Mailer, MongoConnector
from engineering_diplomats.routes import apply_routes
from engineering_diplomats.settings import microsoft_oauth_config, app_config_kwargs
from engineering_diplomats.views.views import SiteHandler


@logme.log
def init_app(logger=None) -> Flask:
	"""Initialize the application"""
	logger.debug("Initializing application from factory.")
	
	app = Flask(
		"engineeringdiplomats[dot]org",
		static_folder=os.environ.get("STATIC_FOLDER"),
		template_folder=os.environ.get("TEMPLATE_FOLDER"),
	)
	app.url_map.strict_slashes = False
	app.config.update(**app_config_kwargs)

	oauth = OAuth(app)
	db = MongoConnector(app)
	mailer = Mailer(Mail(app))

	exporter = stackdriver_exporter.StackdriverExporter(
    	project_id=os.environ.get("GCP_PROJECT"), transport=BackgroundThreadTransport
	)
	tracer = Tracing(app, exporter=exporter)

	microsoft = oauth.remote_app("microsoft", **microsoft_oauth_config)
	site_handler = SiteHandler(db, microsoft, mailer)
	site_handler.get_token = microsoft.tokengetter(site_handler.get_token)
	setattr(app, "site_handler", site_handler)
	
	app = apply_routes(app, site_handler)

	logger.debug("Initialization complete; returning application. ")
	return app


if __name__ == "__main__": # pragma: no cover
	init_app().run(host="0.0.0.0", port=8080, threaded=True, debug=True)
