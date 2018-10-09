# -*- coding: utf-8 -*-

"""View classes for the Flask application."""

import os

from datetime import datetime
from typing import TypeVar, Union
from uuid import uuid4

import logme

from flask import (
	abort,
	flash,
	redirect, 
	request, 
	render_template, 
	session, 
	url_for,
)

from engineering_diplomats.models import (
	User,
	QuestionDocument,
	StudentQueryForm,
)

from engineering_diplomats.utilities import answer_submission, get_events, question_submission 

HTMLBody = TypeVar("HTMLBody", str, str, str)


@logme.log
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
		"""View for home page.
		
		Returns
		-------
		HTMLBody
			The rendered index template.
		"""
		return render_template("index.jinja2")


	def login(self) -> Union[redirect, HTMLBody]:
		"""Login view for Engineering Diplomats.
		Requires Azure API.

		Returns
		-------
		Union[redirect, HTMLBody]
			redirect
				If the user is already logged in or attempting to login.
			HTMLBody
				If the user is attempting to access the login page, the rendered login template.
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


	def logout(self) -> redirect:
		"""Logout view for authenticated users.
		
		Returns
		-------
		redirect
			To the index if the user is logged in.
			To the login page if the user is not yet logged in.
		"""
		if self.is_authorized:
			session.clear()
			flash("Successfully logged out.")
			return redirect(url_for("index"))
		flash("You must login before logging out.")
		return redirect(url_for("login"))


	def questions(self) -> Union[redirect, HTMLBody]:
		"""View for authorized Diplomats to view and answer posted questions.
		
		Returns
		-------
		Union[redirect, HTMLBody]
			redirect
				If an Engineering Diplomat has submitted an answer.
			HTMLBody
				If the user is attempting to access questions page.

		Notes
		------
		Only Engineering Diplomats may view this page.
		"""
		if self.is_authorized:
			if session.get("user").get("is_diplomat") == "True":
				questions = self.db.get_questions()
				if request.method == "GET":
					return render_template("questions.jinja2", questions=questions)
				if request.method == "POST":
					question_id = request.form.get("id")
					request_data = {
						"questions": questions,
						"id": question_id,
						"answer": request.form.get("answer"),
						"diplomat": session.get("user").get("email"),
					}
					answer_submission(self, request_data)
					self.logger.info(f"Sent answer to question {question_id}.")
					self.db.remove_question(question_id)
					self.logger.info(f"Removed question with id {question_id}.")
					flash("Your answer has been submitted. Thanks!")
					return redirect(url_for("questions"))
		flash("Please login first.")
		return redirect(url_for("login"))


	def ask(self) -> Union[redirect, HTMLBody]:
		"""View for any student to post a question.

		Returns
		-------
		Union[redirect, HTMLBody]
			redirect
				If a student has submitted a question or is not logged in.
			HTMLBody
				If the student is attempting to access the ask page, the rendered ask template.
				
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
			elif request.method == "POST":
				if form.validate_on_submit():
					# Add a question to the database
					question_document = QuestionDocument(
						question_id=uuid4().hex,
						submitters_name=form.name.data,
						submitters_email=form.email.data,
						submission_date=datetime.now(),
						question=form.question.data,
					)
					self.db.insert_question(question_document)
					
					# Send a notification email to both the student and the President
					question_submission(self, question_document)

					# Flash and log a success message
					self.logger.info(f"Successfully submitted question {question_document['question_id']}.")
					flash("Thanks for your question! You will receive an email response soon!")
				elif form.recaptcha.errors: # pragma: no cover
					# Flash a captcha error
					self.logger.info("Caught recaptcha error.")
					flash("Please complete the reCAPTCHA.")
				else: # pragma: no cover
					# Flash unknown error
					self.logger.info("Caught unknown error.")
					flash("Error.")
				return redirect(url_for("ask"))
		flash("Please login to ask questions.")
		return redirect(url_for("login"))


	def events(self) -> [redirect, HTMLBody]:
		"""View for event page.
		
		Returns
		-------
		Union[redirect, HTMLBody]
			redirect
				If an Engineernig Diplomats has RSVPed for an event.
			HTMLBody
				If the student is attempting to access the events page, the rendered events template.
				
		Notes
		------
		If a user is an Engineering Diplomat: They have read-write permissions.
		If a user is not an Engineering Diplomat: They have read permissions.
		"""
		return render_template("events.jinja2", events=get_events())


	def resources(self) -> HTMLBody:
		"""View for resources page."""
		return render_template("resources.jinja2")


	def fundraisers(self) -> HTMLBody:
		"""View for fundraisers page."""
		return render_template("fundraisers.jinja2", fundraisers=self.db.get_fundraisers())