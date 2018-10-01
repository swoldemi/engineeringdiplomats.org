# -*- coding: utf-8 -*-

"""View classes for the Flask application."""

import os

from datetime import datetime
from typing import TypeVar, Union
from uuid import uuid4

from flask import (
	abort,
	current_app,
	flash,
	redirect, 
	request, 
	render_template, 
	session, 
	url_for,
)

from engineering_diplomats.models import (
	User, 
	DiplomatAnswerForm,
	QuestionDocument,
	StudentQueryForm,
)

from engineering_diplomats.utilities import get_events, prepare_events

HTMLBody = TypeVar("HTMLBody", str, str, str)


class SiteHandler(object):
	"""Views for engineeringdiplomats.org.

	Attributes
	----------
	db : MongoConnector
		A connection to relevant MongoDB collections.
	oauth : OAuth.oauth.remote_app
		An instance of an authenticated Outlook OAuth client.
	mailer : flask.Mail
		An instance of a configured mailing object.
	"""
	def __init__(self, db, oauth, mailer):
		self.db = db
		self.oauth = oauth
		self.mailer = mailer


	def get_token(self) -> Union[str, None]: # pragma: no cover
		"""Called by flask_oauthlib.client to retrieve current access token.
		
		Returns
		-------
		Union[str, None]
			str
				The user's access token.
			None
				If there is no access token available.
		"""
		return session.get("access_token", None)


	@property
	def is_authorized(self) -> bool:
		"""Authorization property.

		Returns
		-------
		bool
			True if there is an authorized session.
			False if no authentication.
		"""
		if "access_token" in session:
			if session.get("access_token") is not None:
				if "user" in session:
					return True
		return False


	def index(self) -> HTMLBody:
		"""View for home page."""
		return render_template("index.jinja2")


	def login(self) -> redirect:
		"""Login view for Engineering Diplomats.
		Requires Azure API.
		"""
		if self.is_authorized:
			flash("You are already logged in.")
			return redirect(url_for("index"))
		elif request.method == "GET":
			return render_template("login.jinja2")
		session["state"] = str(uuid4())
		return self.oauth.authorize(callback=url_for("authorize", _external=True), state=session["state"])


	def authorize(self) -> Union[redirect, abort]:
		"""Callback for Outlook's OAuth2 validation.
		
		Returns
		-------
		Union[redirect, abort]
			redirect
				A redirect to the home page if the user has successfully logged in.
			abort
				A 404 status code if states are invalid.
		"""
		# Extract states
		request_state = request.args.get("state", default=None)
		session_state = session.get("state", default=None)
		
		# Compare states for validity
		if (request_state != session_state) or (request_state is None):
			abort(404)	
		elif self.is_authorized:
			flash("You are already logged in.")
			return redirect(url_for("index"))

		# If not mocking the API
		if "MOCK" not in os.environ: # pragma: no cover
			response = self.oauth.authorized_response()
		else: 
			response = {
				"access_token": uuid4().hex,
				"email": request.args.get("email"),
				"name": request.args.get("name"),	
			}
		session["access_token"] = response.get("access_token")
		
		# Confirm user authentication by calling the Graph API
		# Create a mock user if running TestSuiteFlask
		headers = {
			"client-request-id": str(uuid4()),
			"return-client-request-id": "true",
		}
		graphdata = self.oauth.get("me", headers=headers).data
		try:
			user = User(graphdata.get("displayName"), graphdata.get("mail").lower())
		except AttributeError:
			user = User(response.get("name"), response.get("email"))

		# Check if the user that is logging in is an Engineering Diplomat
		if user.email in self.db.get_diplomats():
			user.is_diplomat = "True" # TODO: bool condition test
		
		# Define the rest of the session user
		session["user"] = {"name": user.name, "email": user.email, "is_diplomat": user.is_diplomat}
		flash(f"Successfully logged in. Hello {user.name.split(',')[1]}.")
		return redirect(url_for("index"))


	def logout(self) -> Union[redirect, HTMLBody]:
		"""Logout view for authenticated users.
		
		TODO: Catch exceptions here?
		"""
		if self.is_authorized:
			session.clear()
			flash("Successfully logged out.")
			return redirect(url_for("index"))
		flash("You must login before logging out.")
		return redirect(url_for("login"))


	def questions(self) -> HTMLBody:
		"""View for authorized Diplomats to view posted questions.
		
		Notes
		------
		Only Engineering Diplomats may view this page.
		"""
		if self.is_authorized:
			if session["user"]["is_diplomat"] == "True":
				if request.method == "GET":
					return render_template("questions.jinja2", question_list=self.db.get_questions())
				# 1. Get the question id
				# 2. Get the response posted by the Diplomat
				# 3. Get the email associated with the question
				# 4. Create an email response for the question
				# 5. Send the response and delete the question
				print(dict(request.form))
			flash("Only Engineering Diplomats may view the list of questions.")
			return redirect(url_for("index"))
		flash("Please login first.")
		return redirect(url_for("login"))


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
				form=form,
			)
			if form.validate_on_submit():
				# Add a question to the database
				question_doc = QuestionDocument(
					question_id=uuid4().hex,
					submitters_name=form.name.data,
					submitters_email=form.email.data,
					submission_date=datetime.now(),
					question=form.question.data,
				)
				self.db.insert_question(question_doc)
				
				# Send a notification email to both the student and the President
				self.mailer.send_confirmation(question_doc)
				self.mailer.send_notification(question_doc)

				# Flash and log a success message
				current_app.logger.info(f"Successfully submitted question {question_doc['question_id']}")
				flash("Thanks for your question! You will receive an email response soon!")
			elif form.recaptcha.errors: # pragma: no cover
				# Flash a captcha error
				current_app.logger.info("Caught recaptcha error.")
				flash("Please complete the reCAPTCHA.")
			else: # pragma: no cover
				# Flash unknown error
				current_app.logger.info("Caught unknown error.")
				flash("Error.")
			return redirect(url_for("ask"))
		flash("Please login to ask questions.")
		return redirect(url_for("login"))


	def events(self) -> [redirect, HTMLBody]:
		"""View for event page.

		Notes
		------
		If a user is an Engineering Diplomat: They have read-write permissions.
		If a user is not an Engineering Diplomat: They have read permissions.
		"""
		# Get all events and split into 2 groups
		eventsl, eventsr = prepare_events(get_events())
		return render_template("events.jinja2", eventsl=eventsl, eventsr=eventsr)


	def resources(self) -> HTMLBody:
		"""View for resources page."""
		return render_template("resources.jinja2")
