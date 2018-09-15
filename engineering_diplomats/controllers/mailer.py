# -*- coding: utf-8 -*-

"""Classes for sending emails."""

import os

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
    def send_confirmation(self, question_doc: object) -> None:
        """Send a student a confirmation that their question has been received.

        Parameters
        ----------
        question_doc : QuestionDocument
            The metadata of the question that was just submitted.
        """
        kwargs = {
            "subject": "Question Received - engineeringdiplomats.org",
            "recipients": [question_doc.get("submitters_email")],
            "sender" :current_app.config.get("MAIL_USERNAME"),
            "bcc": current_app.config.get("ADMIN"),
        }
        msg = Message(**kwargs)
        msg.html = render_template("_emails/send_confirmation.html", question_doc=question_doc)
        with current_app.app_context():
            self.mailer.send(msg)
    

    @redirect_email_stdout
    def send_notification(self, question_doc: object) -> None:
        """Notify the President that a new question has been received.
        
        Parameters
        ----------
        question_doc : QuestionDocument
            The metadata of the question that was just submitted.
        """
        kwargs = {
            "subject": "New Question Submitted - engineeringdiplomats.org",
            "recipients": [current_app.config.get("ADMIN")],
            "sender": current_app.config.get("MAIL_USERNAME"),
        }
        msg = Message(**kwargs)
        msg.html = render_template("_emails/new_question.html", question_doc=question_doc)
        with current_app.app_context():
            self.mailer.send(msg)


    @redirect_email_stdout
    def send_answer(self, answer: str, question_doc: object) -> None:
        """Send a student the answer to their question.
        
        Parameters
        ----------
        answer : str
            The answer to a students question 
            provided by an Engineering Diplomat.
        question_doc : QuestionDocument
            The metadata of the question that was just submitted.
        
        TODO: Subject line
        """
        kwargs = {
            "subject": "Your question has been answered - Engineering Diplomats",
            "recipients": [student_email],
            "sender": current_app.config.get("MAIL_ACCOUNT"),
            "bcc": os.environ.get("MAINTAINER"),
        }
        msg = Message(**kwargs)
        msg.html = render_template(
            "_emails/send_answer.html",
            question=question,
            answer=answer,
        )
        with current_app.app_context():
            self.mailer.send(msg)
