# -*- coding: utf-8 -*-

"""Utility functions and objects."""

import os

from datetime import datetime
from typing import Dict

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from twilio.rest import Client

from engineering_diplomats.decorators import thread_task

@thread_task
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
		Events as keys w/ list of time and location as values.

	TODO: Turn this function into a generator
	"""
	store = file.Storage("token.json")
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets(os.environ["GOOGLE_CREDS"], SCOPES)
		creds = tools.run_flow(flow, store)
	service = build("calendar", "v3", http=creds.authorize(Http()))

	now = datetime.utcnow().isoformat() + "Z" 
	events_result = service.events().list(
		calendarId='primary', 
		timeMin=now,
		maxResults=100, 
		singleEvents=True,
		orderBy='startTime').execute()
	events = events_result.get("items", [])
	all_events = {}
	for event in events:
		start = event['start'].get("dateTime", event["start"].get("date"))
		all_events[event["summary"]] = [start, event["location"]]
	return all_events
