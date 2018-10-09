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
	listener = ("0.0.0.0", 80)

	try:
		WSGIServer(listener=listener, application=app, log=app.logger).serve_forever()
	except OSError as e:
		logger.exception(e)
		raise
	except Exception as e:
		logger.exception(e)

if __name__ == "__main__":
	main()
