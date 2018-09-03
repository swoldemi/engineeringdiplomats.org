# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField, validators


class StudentQueryForm(FlaskForm):
    """Encapsulation of a form for questions asked by the student."""
    question = StringField("question", [validators.DataRequired()])
    name = StringField("name", [validators.DataRequired()])
    email = StringField("email", [validators.DataRequired()])


class DiplomatAnswerForm(FlaskForm):
    """Encpasulation of a form for answers provided by Engineering Diplomats."""
    pass

