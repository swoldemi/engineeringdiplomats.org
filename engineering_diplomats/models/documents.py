# -*- coding: utf-8 -*-


class QuestionDocument(dict):
	"""Encapsulates the structure of a question to be submitted 
	into the questions collection.
	
	Inherits
	--------
	Type : dict

	Attributes
	-----------
	question_id : UUID
		Unique identifier for retriving the question.
	submitters_name : str
		The name of the student that submitted the question.
	submitters_email : str
		The email of the student that submitted the question.
	question : str
		The question that the student submitted.
	"""
	def __init__(self, *args, **kwargs):
		super(QuestionDocument, self).__init__(*args, **kwargs)
