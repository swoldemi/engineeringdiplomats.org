# -*- coding: utf-8 -*-

from typing import Dict

"""Utility functions and objects."""


def send_text_message(message: str) -> None:
	"""Send testing text messages.
	Currently, this is only used to notify me about 
	periodic tasks.
	
	Twilio's Client class automatically reads sid and token from
	the TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.
	
	Parameters
	----------
	message : str
		The message to be sent by SMS.
	"""
	Client().messages.create(
		to=os.environ["TWILIO_TARGET"], 
		from_=os.environ["TWILIO_NUMBER"],
		body=message,
	)


def get_events() -> Dict[str, list]:
	"""Get all events from my Google Calendar.

	Returns
	-------
	Dict[list]
		Events as keys w/ list of time and location as values
	"""
	pass

