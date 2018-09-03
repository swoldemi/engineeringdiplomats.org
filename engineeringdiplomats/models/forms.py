# -*- coding: utf-8 -*-

"""Front-end form models."""


from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, validators

class StudentQueryForm(FlaskForm):
    """Encapsulation of a form for questions asked by the student."""
    question = StringField("question", [validators.DataRequired()])
    name = StringField("name", [validators.DataRequired()])
    email = StringField("email", [validators.DataRequired()])
    recaptcha = RecaptchaField()


class DiplomatAnswerForm(FlaskForm):
    """Encapsulation of a form for answers provided by Engineering Diplomats."""
    pass

