# -*- coding: utf-8 -*-

"""Classes for sending emails."""

import os

from typing import Tuple

from flask import current_app, render_template
from flask_mail import Message

from engineering_diplomats.decorators import redirect_email_stdout


class Mailer(object):
    """Encapsulates an instance of a mailer which
    shall send emails for the application.

    Attributes
    ----------
    mailer : flask_mail.Mail
        An instance of flask_mail.Mail
    """
    def __init__(self, mailer):
        self.mailer = mailer


    @redirect_email_stdout
    def send_confirmation(self, question_document: object) -> None:
        """Send a student a confirmation that their question has been received.

        Parameters
        ----------
        question_document : QuestionDocument
            The metadata of the question that was just submitted.
        """
        kwargs = {
            "subject": "Question Received - engineeringdiplomats.org",
            "recipients": [question_document.get("submitters_email")],
            "sender": os.environ.get("MAIL_ACCOUNT"),
            "bcc": os.environ.get("MAINTAINER"),
        }
        msg = Message(**kwargs)
        with self.mailer.app.app_context():
            msg.html = render_template("_emails/send_confirmation.html", question_document=question_document)
            self.mailer.send(msg)
    

    @redirect_email_stdout
    def send_notification(self, question_document: object) -> None:
        """Notify the President that a new question has been received.
        
        Parameters
        ----------
        question_document : QuestionDocument
            The metadata of the question that was just submitted.
        """
        kwargs = {
            "subject": "New Question Submitted - engineeringdiplomats.org",
            "recipients": [os.environ.get("MAINTAINER")],
            "sender": os.environ.get("MAIL_ACCOUNT"),
        }
        msg = Message(**kwargs)
        with self.mailer.app.app_context():
            msg.html = render_template("_emails/new_question.html", question_document=question_document)
            self.mailer.send(msg)


    @redirect_email_stdout
    def send_answer(self, answer_data: Tuple[str, object, str]) -> None:
        """Send a student the answer to their question.
        
        Parameters
        ----------
        answer_data : Tuple[str, object, str]
            The answer submitted by an Engineering Diplomat.
            The QuestionDocument object that matches the answered question's id.
            The email of the Engineering Diplomat that submitted the question.
        """
        kwargs = {
            "subject": "Your question has been answered - Engineering Diplomats",
            "recipients": [answer_data[1].get("submitters_email")],
            "sender": os.environ.get("MAIL_ACCOUNT"),
            "bcc": os.environ.get("MAINTAINER"),
        }
        msg = Message(**kwargs)
        with self.mailer.app.app_context():
            msg.html = render_template(
                "_emails/send_answer.html",
                answer=answer_data[0],
                question_document=answer_data[1],
                diplomat=answer_data[2]
            )
            self.mailer.send(msg)
