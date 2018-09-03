# -*- coding: utf-8 -*-

"""View classes for the Flask application."""

import os

from datetime import datetime
from typing import TypeVar, Union
from uuid import uuid4

from flask import (
	abort,
	flash,
	redirect, 
	request, 
	render_template, 
	session, 
	url_for,
)

from ..models import User, StudentQueryForm, QuestionDocument

HTMLBody = TypeVar("HTMLBody", str, str, str)


class SiteHandler(object):
	"""Views for engineeringdiplomats.com.

	Attributes
	----------
	db : MongoConnector
		A connection to relevant MongoDB collections.
	oauth : OAuth.oauth.remote_app
		An instance of an authenticated Outlook OAuth client.
	"""
	def __init__(self, db, oauth):
		self.__url__ = "http://engineeringdiplomats.org"
		self.db = db
		self.oauth = oauth


	def get_token(self):
		"""Called by flask_oauthlib.client to retrieve current access token."""
		return (session.get("access_token"), "")


	@property
	def is_authorized(self) -> bool:
		"""Authorization property.

		Returns
		-------
		bool
			True if there is a authorized session.
			False if no authentication.
		"""
		if "access_token" in session:
			if session["access_token"] is not None:
				if "user" in session:
					return True
		return False


	def index(self) -> HTMLBody:
		"""View for home page."""
		try:
			user_data = session["user"]
		except KeyError:
			user_data = None
		return render_template("index.jinja2", user_data=user_data)


	def login(self) -> redirect:
		"""Login view for Engineering Diplomats.
		Requires Azure API.
		"""
		if self.is_authorized:
			# flash("You are already logged in.")
			return redirect(url_for("index"))

		session["state"] = str(uuid4())
		return self.oauth.authorize(callback=url_for("authorize", _external=True), state=session["state"])


	def authorize(self) -> redirect:
		"""Callback for Outlook's OAuth2 validation. 
		Only allow authorized Engineering Diplomats to login.
		
		Raises
		------
		StateException
		"""
		if self.is_authorized:
			#print("You are already logged in.")
			#flash("You are already logged in.")
			#return redirect(url_for("index"))
			return "You are already logged in."

		if str(session["state"]) != str(request.args["state"]):
			raise StateException("State returned to a redirect URL that does not match!")
		response = self.oauth.authorized_response()
		session["access_token"] = response["access_token"]
		
		# Confirm user authentication by calling the Graph API
		headers = {
			"client-request-id": str(uuid4()),
			"return-client-request-id": "true",
		}
		graphdata = self.oauth.get("me", headers=headers).data
		user = User(graphdata["displayName"], graphdata["mail"])
		if user.email.lower() in self.db.get_diplomats():
			user.is_diplomat = True
		session["user"] = {"name": user.name, "email": user.email, "is_diplomat": user.is_diplomat}
		flash(f"Welcome {user.name.split(',')[1]}")
		return redirect(url_for("index"))


	def logout(self) -> Union[redirect, HTMLBody]:
		"""Logout view for authenticated users."""
		if self.is_authorized:
			session.clear()
			return render_template("logout.jinja2")
		return "You must login before logging out."


	def questions(self) -> HTMLBody:
		"""View for authorized Diplomats to view posted questions."""
		if self.is_authorized:
			if session["user"]["is_diplomat"]:
				if request.method == "GET":
					return render_template("questions.jinja2", question_list=self.db.get_questions())
				# 1. Get the question id
				# 2. Get the response posted by the Diplomat
				# 3. Get the email associated with the question
				# 4. Create an email response for the question
				# 5. Send the response and delete the question
				print(dict(request.form))
		#return redirect(url_form("login"))


	def ask(self) -> Union[redirect, HTMLBody]:
		"""View for any student to post a question.

		Notes
		------
		Both Diplomats and students have the same permissions here.
		"""
		form = StudentQueryForm()
		if self.is_authorized:
			if request.method == "GET":
				return render_template(
				"ask.jinja2", 
				name=session["user"]["name"], 
				email=session["user"]["email"],
				form=form,
			)

			# Add a question to the database
			question_doc = QuestionDocument(
				question_id=uuid4().hex,
				submitters_name=form.name.data,
				submitters_email=form.email.data,
				submission_date=datetime.now(),
				question=form.question.data,
			)

			self.db.insert_question(question_doc)
			
			# Flash a success message
			flash("Thanks for your question! You will receive an email response soon!")
			return redirect(url_for("ask"))
		return "You must login to ask a question."


	def events(self) -> [redirect, HTMLBody]:
		"""View for event page.

		Notes
		------
		If a user is an Diplomat: They have u+rw- permissions.
		If a user is not an Diplomats: They have u+r-- permissions.
		"""
		if self.is_authorized:
			if session["user"]["is_diplomat"]:
				if request.method == "GET":
					# Get all events from database
					events = self.db.get_events()
					return render_template("rsvp.jinja2", events=events)
				print(dict(request.form))
				# Extract selected times,
				# Extract name and email
				# Extract selected event ID
				return redirect(url_for("events"))
		return redirect(url_for("index"))


	def resources(self) -> HTMLBody:
		"""View for resources page."""
		return render_template("resources.jinja2")


class StateException(Exception):
	"""Raised when session state and redirect state are tampered."""
	pass