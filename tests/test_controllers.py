# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import uuid4

import pytest

from bson.objectid import ObjectId
from flask_mail import Mail

from engineering_diplomats.controllers import MongoConnector, Mailer
from engineering_diplomats.models import QuestionDocument


class TestSuiteControllers(object):
    
    def test_db(self, app):
        """Test database operations.
        
        Parameters
        ----------
        app : flask.Flask
            Instance of the application injected by pytest.
        """
        mongo_connector = MongoConnector(app)

        # Find my email in the list of Diplomats' emails
        assert "simon.woldemichael@ttu.edu" in mongo_connector.get_diplomats()

        # Create a new question
        question_doc = QuestionDocument(
            question_id=uuid4().hex,
            submitters_name="Simon Woldemichael",
            submitters_email="simon.woldemichael@ttu.edu",
            submission_date=datetime.now(),
            question="How do I study abroad?",
        )

        # Insert question into database
        assert type(mongo_connector.insert_question(question_doc)) is ObjectId

        # Make sure recently inserted question exists when get call is made
        found = False
        for document in mongo_connector.get_questions():
            if document["question_id"] == question_doc["question_id"]:
                found = True
        assert found

        # Delete the question that was just added
        assert mongo_connector.remove_question(question_doc["question_id"])


    def test_mailer(self, app):
        """Test mailing controller.

        Parameters
        ----------
        app : flask.Flask
            Instance of the application injected by pytest.
        """
        mailer = Mailer(Mail(app))
        
        question_doc = QuestionDocument(
            question_id=uuid4().hex,
            submitters_name="Simon Woldemichael",
            submitters_email="simon.woldemichael@ttu.edu",
            submission_date=datetime.now(),
            question="How do I study abroad?",
        )

        assert mailer.send_notification(question_doc) is None
        assert mailer.send_confirmation(question_doc) is None
        assert mailer.send_answer("Answer", question_doc) is None
            