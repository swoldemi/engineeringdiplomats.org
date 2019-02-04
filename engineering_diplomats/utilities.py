# -*- coding: utf-8 -*-

"""Utility functions and objects."""

import os

from datetime import datetime, timedelta
from typing import List, Tuple, Union

from dateutil.parser import parse
from twilio.rest import Client

from engineering_diplomats.decorators import thread_task
from engineering_diplomats.settings import service

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


@thread_task
def answer_submission(handler: object, request_data: dict) -> None:
    """Performs answer submission logic on a new thread.
    Mainly to mitigate how slow SMTP calls are.

    Parameters
    -----------
    handler : SiteHandler
        Active instance of the SiteHandler.

    request_data : dict
        Current list of questions, the submitted question's id, 
        the submitted answer, and the diplomat's email. 
    """
    question_id = request_data.get("id")
    questions = request_data.get("questions")
    for question in questions:
        if question_id == question.get("question_id"):
            question_document = question
            break
    
    answer_data = (
        request_data.get("answer"),
        question_document,
        request_data.get("diplomat"),
    )
    handler.mailer.send_answer(answer_data)


@thread_task
def question_submission(handler: object, question_document: object) -> None:
    """Performs question submission logic on a new thread.
    Mainly used to mitigate how slow SMTP exchanges are.

    Parameters
    ----------
    handler : SiteHandler
        Active instance of the SiteHandler.
    
    question_document : QuestionDocument
        The metadata of the question that was just submitted.

    """
    handler.mailer.send_confirmation(question_document)
    handler.mailer.send_notification(question_document)


def get_events() -> Union[List[List], List[None]]:
	"""Get all events from my Google Calendar.

	Returns
	-------
	Union[List[List], List[None]]
		List[List]
			A list of event entries indexed as follows:
			- 0 : str
			  The name of the events.
			- 1 : str
			  The start time of the event.
			- 2 : str 
			  The location of the event.
			- 3 : List[str] 
			  The diplomats attending the event.
			- 4: str
			  The unique event ID
		List[None]:
			If there are no events in the Google Calendar.

	Notes
	------
	event.attendees denotes that diplomats that have RSVPed for an event
	"""
	now = datetime.utcnow().isoformat() + "Z" 
	events_result = service.events().list(
		calendarId="primary", 
		timeMin=now,
		maxResults=100, 
		singleEvents=True,
		orderBy="startTime").execute()
	all_events = []
	for event in events_result.get("items", []):
		start_date, *start_time = parse(event["start"].get("dateTime")).strftime("%m/%d/%Y %I:%M %p").split(" ")
		start_time = " ".join(start_time)
		start = f"{start_date} at {start_time}"
		
		# Ignore calendar entries that do no have a location
		if "location" in event: # pragma: allow
			entry = [event["summary"], start, event["location"], event.get("attendees", None), event.get("id")]
			if entry[3] is not None: # pragma: allow
				entry[3] = [e["email"] for e in entry[3]]
			all_events.append(entry)
	return all_events


def update_event(email: str, event_id: str, unregister: bool) -> str:
	"""Update the RSVP of an event with a new attendee.

	Parameters
	----------
	email : str
		The email of the diplomat RSVPing
	event_id : str
		The event ID of the information session/event being RSVPed for
	unregister : bool
		A flag to denote if the request being made is to unregister a diplomat
	
	Returns
	--------
	str
		Result message of the update
	"""
	request_body = {
		"sendUpdates": "none",
	}

	# Get all attendees
	all_attendees = service.events().get(
		calendarId="primary", 
		eventId=event_id
		).execute().get("attendees")
	
	if all_attendees is None:
		all_attendees = []
	else:
		all_attendees = [a.get("email") for a in all_attendees]
	
	if unregister:
		# Remove the attendee 
		all_attendees.remove(email)
		request_body["attendees"] = [{"email": email} for email in all_attendees]
		flash_message = "You are now unregistered for this event."
	else:
		# Add the new attendee
		all_attendees.append(email)
		request_body["attendees"] = [{"email": e} for e in all_attendees]
		flash_message = """
			You are RSVPed for this event. 
			If this event is an on-campus information session,
			please remember to review the presentation for this 
			information session in advance.
			"""
	
	try:
		service.events().patch(
			calendarId="primary",
			eventId=event_id,
			body=request_body,
		).execute()
		state = "RSVPed" if not unregister else "cancelled"
		send_text_message(f"{email} has successfully {state} for event {event_id}.")
		return flash_message

	except Exception as e:
		error_message = f"Error: {e}"
		send_text_message(f"Error: {e}")
		return error_message

