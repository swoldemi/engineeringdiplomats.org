# -*- coding: utf-8 -*-

"""Tests for helper functions and specific decorators."""

import threading

from time import sleep

from engineering_diplomats.utilities import get_events, prepare_events, send_text_message

import pytest

class TestSuiteOther(object):

    def test_send_text(self):
        """Send a text message. Sleeps current thread until
        the task thread used to send the text has died.
        """
        assert send_text_message("Hi") is None
        is_alive = False
        task_thread = None
        for thread in threading.enumerate():
            if thread.name == "send_text_message":
                task_thread = thread
                break
        while task_thread.is_alive():
            sleep(1)

        assert not task_thread.is_alive()


    def test_get_events(self):
        """Get all events from 
        ttuengineeringdiplomats@gmail.com's Google Calendar."""
        all_events = get_events()
        for event in all_events:
            assert len(event) is 4
        

    def test_prepare_events(self):
        
        prepared_events = prepare_events(get_events())
        assert len(prepared_events) is 2
        
        eventsl, eventsr = prepared_events
        assert len(eventsl) is len(eventsr)
        assert len(eventsl) + len(eventsr)  >= len(get_events())
