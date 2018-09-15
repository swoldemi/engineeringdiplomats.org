# -*- coding: utf-8 -*-

import logging
import os

from typing import List

from flask import current_app
from pymongo import MongoClient
from pymongo.errors import ExecutionTimeout, OperationFailure, ServerSelectionTimeoutError

from engineering_diplomats.models import QuestionDocument

class MongoConnector(object):
	"""Encapsulates a connection to MongoDB.

	Attributes
	-----------
	logger : logging.Logger
		Logger for database exceptions
	client : pymongo.MongoClient
		An authenticated instance of MongoClient.
	diplomats_collection : pymongo.collection
		Database collection used for current Engineering Diplomats
	questions_collection : pymongo.collection
		Database collection for submitted questions
	"""
	def __init__(self, app):
		self.logger = logging.getLogger(__name__)
		self.errors = (ExecutionTimeout, OperationFailure, ServerSelectionTimeoutError)
		try:
			url = f"mongodb://{os.environ['MONGO_USERNAME']}:{os.environ['MONGO_PASSWORD']}@{os.environ['MONGO_HOST']}:{os.environ['MONGO_PORT']}/"
			self.client = MongoClient(url)
		except self.errors as e:
			self.logger.exception(e)
			raise
		
		self.diplomats_collection = self.client.diplomats.registered_diplomats
		self.questions_collection = self.client.diplomats.questions

	
	def get_diplomats(self) -> List[str]:
		"""Return the emails of all of the registered Engineering Diplomats.

		Returns
		-------
		List[str]
			List of all emails
		"""
		with current_app.app_context():
			try:
				return self.diplomats_collection.find({})[0]["diplomat_emails"]
			except self.errors as e:
				self.logger.exception(e)
				raise
	

	def insert_question(self, data: QuestionDocument) -> None:
		"""Inserts an inquiry into the database.
		
		Parameters
		-----------
		data : QuestionDocument
			The question and metadata to be inserted into the document
		"""
		with current_app.app_context():
			try:
				assert self.questions_collection.insert_one(data).inserted_id
			except self.errors + (AssertionError,) as e:
				self.logger.exception(e)
				raise
	

	def get_questions(self) -> List[dict]:
		"""Get all of the unanswered questions that exist in the database."""
		pass
	

	def remove_question(self, id) -> None:
		"""Remove a question that has been answered."""
		pass

