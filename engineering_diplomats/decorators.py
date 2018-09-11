# -*- coding: utf-8 -*-

"""Custom decorator functions."""

import atexit

from contextlib import redirect_stderr, redirect_stdout
from functools import wraps
from threading import Thread
from typing import Callable

from engineering_diplomats.settings import emails_log_file


def thread_task(f: Callable) -> Callable:
	"""Defines a wrapper that will decorate a function.
	
	Parameters
	----------
	f : Callable
		The function to be wrapped.

	Returns
	-------
	Callable
		A function that will be ran on a seperate thread when it is called.
	"""
	@wraps(f)
	def wrapper(*args, **kwargs):
		thread = Thread(target=f, name=f.__name__, args=args, kwargs=kwargs)
		thread.daemon = True
		thread.start()
	return wrapper


def redirect_email_stdout(f: Callable) -> Callable:
	"""Defines a wrapper that will decorate a function.

	Parameters
	----------
	f : Callable
		The function to be wrapped.

	Returns
	-------
	Callable
		A function which will have its contents written to email.log.
		This decorator should only be used for send_email() functions
		within the boarding_mailers module.
	"""
	@wraps(f)
	def wrapper(*args, **kwargs):
			with redirect_stdout(emails_log_file):
				with redirect_stderr(emails_log_file):
					f(*args, **kwargs)
	return wrapper

atexit.register(lambda: emails_log_file.close())