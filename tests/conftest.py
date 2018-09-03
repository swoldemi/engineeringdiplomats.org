# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(1, os.path.join(sys.path[0], ".."))

import pytest

from application import init_app

@pytest.fixture
def app():
    """
    Flask application client test fixture.

    Returns
    -------
    flask.Flask
        An instance of the web app.
    """
    app = init_app()
    app.debug = True
    app.threaded = True
    return app
