# -*- coding: utf-8 -*-

import os
import sys

import pytest

from flask import url_for

class TestSuiteFlask(object):

    def test_environment(self):
        """Test environment state."""
        assert os.environ.get("FLASK_ENV") == "development"
        assert os.environ.get("SECRET_KEY") is not None
        assert bool(int(os.environ.get("DEBUG"))) is True


    def test_views_unauthenticated(self, client):
        """Test that views yeild expected status codes.
        
        Parameters
        ----------
        client : Client
            An instance of werkzeug.test.Client
        """
        assert client.get(url_for("index")).status_code == 200
        assert client.get(url_for("resources")).status_code == 200
        assert client.get(url_for("ask")).status_code == 302
        assert client.get(url_for("logout")).status_code == 302
        assert client.get(url_for("authorize")).status_code == 404
        