# -*- coding: utf-8 -*-

import os
import sys

import pytest

from flask import request, url_for

OK = 200
NOT_FOUND = 404
REDIRECT = 302 # "FOUND"


class TestSuiteFlask(object):

	def test_environment(self):
		"""Test environment state."""
		assert os.environ.get("FLASK_ENV") == "development"
		assert os.environ.get("SECRET_KEY") is not None
		assert bool(int(os.environ.get("DEBUG"))) is True


	def test_views_unauthenticated(self, client, app):
		"""Test that views yeild expected status codes before 
		students or Engineering Diplomats have logged in.
		
		Parameters
		----------
		client : Client
			An instance of werkzeug.test.Client

		app : flask.Flask
            Instance of the application injected as a test fixture
            by pytest.
		"""
		assert client.get(url_for("index")).status_code == OK
		assert client.get(url_for("resources")).status_code == OK
		assert client.get(url_for("login")).status_code == OK
		assert client.get(url_for("ask")).status_code == REDIRECT
		assert client.get(url_for("logout")).status_code == REDIRECT
		assert client.get(url_for("questions")).status_code == REDIRECT
		assert client.get(url_for("authorize")).status_code == NOT_FOUND
		assert app.site_handler.is_authorized is False
