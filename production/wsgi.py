# -*- coding: utf-8 -*-

import os
import sys

import logme

from gevent.pywsgi import WSGIServer

from engineering_diplomats.main import init_app


@logme.log
def main(logger=None) -> None:
	"""Main routine to initialize and start the production environment."""
	
	app = init_app()
	os.environ["FLASK_ENV"] = "production"
	os.environ["DEBUG"] = "0"
	here = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	logger.info(f"Running from {here}")
	app.site_handler.callback = "https://www.engineeringdiplomats.org/authorize"
	app.site_handler.external = True
	logger.info(f"OAuth2 callback defined as: {app.site_handler.callback}")
	logger.info(f"Redirect external set to: {app.site_handler.external}")
	try:
		WSGIServer(
			listener=("0.0.0.0", 8080), 
			application=app,  
			log=logger,
		).serve_forever()
	# Don't need to do much on exception as recovery is handled by Kubernetes scheduler
	except OSError as e:
		logger.exception(e)
		raise
	except Exception as e:
		logger.exception(e)
		raise
if __name__ == "__main__":
	main()
