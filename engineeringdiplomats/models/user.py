# -*- coding: utf-8 -*-

class User(object):
	"""Encapsulates a logged in users data

	Attributes 
	----------
	name : str
		The name of the user that logged in.
	email : str
		The outlook email of the user that logged in.
	is_diplomat : bool
		True | The logged in user is an Engineering Diplomat.
		False | The logged in user is not an Engineering Diplomat.
	"""
	def __init__(self, name, email):
		self.name = name
		self.email = email 
		self.is_diplomat = False
