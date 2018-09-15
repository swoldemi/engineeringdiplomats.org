# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import uuid4

import pytest

from engineering_diplomats.models import User, QuestionDocument

name = "Simon Woldemichael"
email = "simon.woldemichael@ttu.edu"


class TestSuiteModels(object):

    def test_user(self):
        """Test that user instances are initialized
        correctly.

        TODO: Data validation.
        """
        user = User(name, email)

        assert user.name == "Simon Woldemichael"
        assert user.email == "simon.woldemichael@ttu.edu"
        assert user.is_diplomat is False
        user.is_diplomat = True
        assert user.is_diplomat is True
        

    def test_documents(self):
        """Test initialziations of MongoDB documents.
        
        TODO: Data validation.
        """

        question_document = QuestionDocument(
            question_id=uuid4().hex,
            submitters_name=name,
            submitters_email=email,
            submission_date=datetime.now(),
            question="What?",
        )

        assert isinstance(question_document, dict)

    