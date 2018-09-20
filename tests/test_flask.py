# -*- coding: utf-8 -*-

import os
import sys

import pytest

from flask import request, session, url_for

OK = 200
NOT_FOUND = 404
REDIRECT = 302 # "FOUND"


class TestSuiteFlask(object):
	
	os.environ["MOCK"] = "1"

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
		assert client.get(url_for("events")).status_code == OK
		assert client.get(url_for("ask")).status_code == REDIRECT
		assert client.get(url_for("logout")).status_code == REDIRECT
		assert client.get(url_for("questions")).status_code == REDIRECT
		assert client.get(url_for("authorize")).status_code == NOT_FOUND

		assert app.site_handler.is_authorized is False


	def test_views_authenticated(self, client, app):
		"""Test that views yeild expected status codes after
		students or Engineering Diplomats have logged in.

		Parameters
		----------
		client : Client
			An instance of werkzeug.test.Client

		app : flask.Flask
            Instance of the application injected as a test fixture
            by pytest.
		"""
		assert bool(int(os.environ.get("MOCK")))
		response = client.post(url_for("login"))

		state = response.location.split("state=")[1]
		assert "state" in session

		query_string = {
			"state": state,
			"name": "Woldemichael, Simon",
			"email": "simon.woldemichael@ttu.edu",
		}
		
		response = client.get(url_for("authorize"), query_string=query_string)
		assert response.status_code == REDIRECT
		assert "user" in session
		
		assert client.get(url_for("login")).status_code == REDIRECT
		assert "user" in session
		
		response = client.get(url_for("authorize"), query_string=query_string)
		assert response.status_code == REDIRECT
		assert "user" in session
		
		# Test /ask while logged in
		assert client.get(url_for("ask")).status_code == OK

		data = {
			"name": query_string.get("name"),
			"email": query_string.get("email"),
			"question": "What is Study Abroad?",
		}

		assert client.post(url_for("ask"), data=data)
		
		# Logout
		assert client.get(url_for("logout")).status_code == REDIRECT
		assert "state" not in session
		assert "user" not in session
