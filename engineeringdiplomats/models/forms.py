# -*- coding: utf-8 -*-

from wtforms import Form, validators


class StudentQueryForm(Form):
    """Encapsulation of a form for questions asked by the student."""
    question = StringField("Question", [validators.DataRequired()])
    name = StringField("Name", [validators.DataRequired()])
    email = StringField("Email Address", [validators.DataRequired()])
