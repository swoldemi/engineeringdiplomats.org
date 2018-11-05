# -*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
from uuid import uuid4

import pytest

from bson.objectid import ObjectId
from flask_mail import Mail

from engineering_diplomats.controllers import Mailer, MemcachedConnector, MongoConnector
from engineering_diplomats.models import QuestionDocument


class TestSuiteControllers(object):
	
	def test_db(self, app):
		"""Test database operations.
		
		Parameters
		----------
		app : flask.Flask
			Instance of the application injected by pytest.
		"""
		mongo_connector = MongoConnector(app)

		# Find my email in the list of Diplomats' emails
		assert "simon.woldemichael@ttu.edu" in mongo_connector.get_diplomats()

		# Create a new question
		question_document = QuestionDocument(
			question_id=uuid4().hex,
			submitters_name="Simon Woldemichael",
			submitters_email="simon.woldemichael@ttu.edu",
			submission_date=datetime.now(),
			question="How do I study abroad?",
		)

		# Insert question into database
		assert type(mongo_connector.insert_question(question_document)) is ObjectId

		# Make sure recently inserted question exists when get call is made
		found = False
		for document in mongo_connector.get_questions():
			if document["question_id"] == question_document["question_id"]:
				found = True
		assert found

		# Delete the question that was just added
		assert mongo_connector.remove_question(question_document["question_id"])

		# Get points for a Diplomat
		assert mongo_connector.get_points(question_document["submitters_email"])


	def test_mailer(self, app):
		"""Test mailing controller.

		Parameters
		----------
		app : flask.Flask
			Instance of the application injected by pytest.
		"""
		# Instantiate a new Mailer
		mailer = Mailer(Mail(app))
		
		# Create a new question document
		question_document = QuestionDocument(
			question_id=uuid4().hex,
			submitters_name="Woldemichael, Simon",
			submitters_email="simon.woldemichael@ttu.edu",
			submission_date=datetime.now(),
			question="How do I study abroad?",
		)

		# Send emails using the data provided in the question document
		assert mailer.send_notification(question_document) is None
		sleep(2)
		assert mailer.send_confirmation(question_document) is None
		sleep(2)

		# Create answer data and send an answer
		answer_data = (
			"Answer",
			question_document,
			"simon.woldemichael@ttu.edu",
		)
		assert mailer.send_answer(answer_data) is None


	def test_cache(self):
		"""Test the memecached client."""
		cache_client = MemcachedConnector().client
		cache_client.set("key", "hello")
		assert cache_client.get("key") == "hello"
