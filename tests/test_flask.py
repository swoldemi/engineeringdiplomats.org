# -*- coding: utf-8 -*-

import os
import sys

from time import sleep

import pytest

from flask import current_app, request, session, url_for
from engineering_diplomats.controllers import MongoConnector

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
		assert client.get(url_for("fundraisers")).status_code == OK
		assert client.get(url_for("points")).status_code == REDIRECT
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
		# Make sure we're mocking Oauth
		assert bool(int(os.environ.get("MOCK")))
		response = client.post(url_for("login"))

		# Extract state
		state = response.location.split("state=")[1]
		assert "state" in session

		# Define query parameters
		query_string = {
			"state": state,
			"name": "Woldemichael, Simon",
			"email": "simon.woldemichael@ttu.edu",
		}
		
		# Send query parameters in authorization request
		response = client.get(url_for("authorize"), query_string=query_string)
		assert response.status_code == REDIRECT
		assert "user" in session
		
		# Make sure we are redirected because we are already logged in
		assert client.get(url_for("login")).status_code == REDIRECT
		assert "user" in session
		response = client.get(url_for("authorize"), query_string=query_string)
		assert response.status_code == REDIRECT
		assert "user" in session
		
		# Test /ask while logged in
		assert session.get("user").get("is_diplomat") == "True"
		assert client.get(url_for("ask")).status_code == OK

		question = "What is Study Abroad?"
		data = {
			"name": query_string.get("name"),
			"email": query_string.get("email"),
			"question": question,
		}
		assert client.post(url_for("ask"), data=data)
		
		# Sleep to give worker thread some time to complete SMTP exchanges
		print("Sleeping...")
		sleep(20)	
		print("Awake.")

		# Get the question_id of the question that was just asked
		mongo_connector = MongoConnector(app)
		question_id = mongo_connector.questions_collection.find_one({"question": question}).get("question_id")
		assert question_id is not None

		data = {
			"id": question_id,
			"answer": "Study Abroad is awesome!",
		}
		# Test /questions 
		assert client.get(url_for("questions")).status_code == OK
		assert client.post(url_for("questions"), data=data).status_code == REDIRECT

		# Test /points while logged in
		assert client.get(url_for("points")).status_code == OK

		# Sleep to give worker thread some time to complete SMTP exchanges
		print("Sleeping... ")
		sleep(20)
		print("Awake.")

		# Logout
		assert client.get(url_for("logout")).status_code == REDIRECT
		assert "state" not in session
		assert "user" not in session
