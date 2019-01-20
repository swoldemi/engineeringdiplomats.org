# -*- coding: utf-8 -*-

import logging
import os

from typing import List

import logme

from bson.objectid import ObjectId
from pymongo import MongoClient
from pymongo.cursor import CursorType
from pymongo.errors import ExecutionTimeout, OperationFailure, ServerSelectionTimeoutError

from engineering_diplomats.models import QuestionDocument
from engineering_diplomats.controllers.cache import MemcachedConnector

@logme.log
class MongoConnector(object):
	"""Encapsulates a connection to MongoDB.

	Attributes
	-----------
	app : flask.Flask
		equivalent to flask.current_app
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
		self.app = app
		self.errors = (ExecutionTimeout, OperationFailure, ServerSelectionTimeoutError)
		try:
			uri = f"mongodb+srv://{os.environ.get('MONGO_USERNAME')}:{os.environ.get('MONGO_PASSWORD')}"
			uri = f"{uri}@diplomats-cluster0-o6453.mongodb.net/diplomats?retryWrites=true"
			self.client = MongoClient(uri)
		except self.errors as e: # pragma: no cover
			self.logger.exception(e)
			raise
		
		self.diplomats_collection = self.client.diplomats.registered_diplomats
		self.questions_collection = self.client.diplomats.questions
		self.fundraisers_collection = self.client.diplomats.fundraisers
		self.cache = MemcachedConnector().client
	
	def get_diplomats(self) -> List[str]:
		"""Return the emails of all of the registered Engineering Diplomats.

		Returns
		-------
		List[str]
			List of all emails
		"""
		with self.app.app_context():
			try:
				return self.diplomats_collection.find({})[0]["diplomat_emails"]
			except self.errors as e: # pragma: no cover
				self.logger.exception(e)
				raise
	

	def insert_question(self, data: QuestionDocument) -> ObjectId:
		"""Inserts an inquiry into the database.
		
		Parameters
		-----------
		data : QuestionDocument
			The question and metadata to be inserted into the document

		Returns
		-------
		bson.objectId.ObjectId
			The ObjectId of the document that was just created.
		"""
		with self.app.app_context():
			try:
				return self.questions_collection.insert_one(data).inserted_id
			except self.errors as e: # pragma: no cover
				self.logger.exception(e)
				raise
	

	def get_questions(self) -> list:
		"""Get all of the unanswered questions that exist in the database.
		
		Returns
		--------
		pymongo.cursor.Cursor : CursorType
			A cursor for the collection which contains all of the question documents.
		"""			
		with self.app.app_context():
			try:
				questions = self.questions_collection.find({})
			except self.errors as e: # pragma: no cover
				self.logger.exception(e)
				raise
		return [question for question in questions]


	def remove_question(self, id) -> bool:
		"""Remove a question that has been answered.
		
		Parameters
		----------
		id : uuid4
			The question_id of the question to be removed

		Returns
		-------
		pymongo.results.DeleteResult.acknowledged : bool 
			Database acknowledgement that the document was deleted. 
		"""
		with self.app.app_context():
			try:
				return self.questions_collection.delete_one({"question_id": id}).acknowledged
			except self.errors as e: # pragma: no cover
				self.logger.exception(e)
				raise

	
	def get_fundraisers(self) -> CursorType:
		"""Get all upcoming fundraisers from fundraisers collection.
		
		Returns
		--------
		pymongo.cursor.Cursor : CursorType
			A cursor for the collection which contains all of the question documents.
		"""
		with self.app.app_context():
			try:
				return self.fundraisers_collection.find({})
			except self.errors as e: # pragma: no cover
				self.logger.exception(e)
				raise


	def get_points(self, email) -> dict:
		"""Get all upcoming fundraisers from fundraisers collection.
		
		Returns
		--------
		dict
			Document containing a diplomat's points and event attendance.
		"""
		with self.app.app_context():
			try:
				return self.diplomats_collection.find_one({"email": email})
			except self.errors as e: # pragma: no cover
				self.logger.exception(e)
				raise
