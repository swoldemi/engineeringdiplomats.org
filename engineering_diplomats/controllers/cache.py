# -*- coding: utf-8 -*-

import logging
import os

import bmemcached


class MemcachedConnector(object):
	"""Provides a connection to a cloud-based memcached instance.

	Attributes
	----------
	client : bmemcached.Client
		Authenticated and connected memcached instance.

	See Also
	--------
	https://app.redislabs.com/#/bdb/tabs/conf/9021895 (Private)
	https://realpython.com/python-memcache-efficient-caching/
	"""
	def __init__(self):
		self.client = bmemcached.Client(
			(f"{os.environ.get('MEMCACHED_HOST')}:{os.environ.get('MEMCACHED_PORT')}"), 
			os.environ.get("MEMCACHED_USERNAME"),
			os.environ.get("MEMCACHED_PASSWORD"),
		)
