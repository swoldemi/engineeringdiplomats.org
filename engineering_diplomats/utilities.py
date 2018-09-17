# -*- coding: utf-8 -*-

"""Utility functions and objects."""

import os

from datetime import datetime
from typing import List, Tuple, Union

from googleapiclient.discovery import build
from httplib2 import Http
from numpy import array_split
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


def get_events() -> Union[List[List], List[None]]:
	"""Get all events from my Google Calendar.

	Returns
	-------
	Union[List[List], List[None]]
		List[List]
			A list of event entries indexed as follows:
			- 0 : str
			  - The name of the events.
			- 1 : str
			  - The start time of the event.
			- 2 : str 
			  - The location of the event.
			- 3 : List[str] 
			  - The diplomats attending the event.
		List[None]:
			If there are no events in the Google Calendar.

	Notes
	------
	Attendes denotes that diplomats that have RSVP'd for an event
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
		calendarId="primary", 
		timeMin=now,
		maxResults=100, 
		singleEvents=True,
		orderBy="startTime").execute()
	events = events_result.get("items", [])
	all_events = []
	for event in events:
		start_time = event["start"].get("dateTime", event["start"].get("date"))
		entry = [event["summary"], start_time, event["location"], event.get("attendees", None)]
		if entry[3] is not None:
			entry[3] = [e["email"] for e in entry[3]]
		all_events.append(entry)
	return all_events


def prepare_events(events: List[List[str]]) -> Tuple[List[List[str]], List[List[str]]]:
	"""Split events into 2 equally sized groups.

	Parameters
	----------
	events : List[List[str]]:
		The events retrieved from the get_events utility function.
	
	Returns
	-------
	Tuple[List[List[str]], List[List[str]]]
		Unpackable tuple of the two event groups of equal length.
	"""

	eventsl, eventsr = array_split(events, 2)
	eventsl = eventsl.tolist()
	eventsr = eventsr.tolist()
	if len(eventsl) > len(eventsr):
		for x in range(len(eventsl) - len(eventsr)):
			eventsr.append([None, None, None, None])
	elif len(eventsl) < len(eventsr):
		for x in range( len(eventsr) - len(eventsl)):
			eventsl.append([None, None, None, None])
	return eventsl, eventsr


def update_event(event: dict) -> None:
	"""Update the RSVP of an event.


	Parameters
	----------
	event : dict
		The event to be updated.
	"""
	pass