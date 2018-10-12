# -*- coding: utf-8 -*-

"""Settings and config."""

import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

microsoft_oauth_config = {
    "consumer_key" : os.environ.get("AZURE_ID"),
    "consumer_secret" : os.environ.get("AZURE_KEY"),
    "request_token_params" : {"scope": "User.Read"},
    "base_url" : "https://graph.microsoft.com/v1.0/",
    "request_token_url" : None,
    "access_token_method" : "POST",
    "access_token_url" : "https://login.microsoftonline.com/organizations/oauth2/v2.0/token",
    "authorize_url" : "https://login.microsoftonline.com/organizations/oauth2/v2.0/authorize",
}

app_config_kwargs = {
	"SECRET_KEY": os.environ.get("SECRET_KEY"),
	"MAIL_SERVER": os.environ.get("MAIL_SERVER"),
	"MAIL_PORT": int(os.environ.get("MAIL_PORT")),
    "MAIL_USE_SSL": True,
	"MAIL_USERNAME": os.environ.get("MAIL_ACCOUNT"),
	"MAIL_PASSWORD": os.environ.get("MAIL_PASS"),
    "ADMIN": os.environ.get("MAINTAINER"),
    "RECAPTCHA_PUBLIC_KEY": os.environ.get("RECAPTCHA_PUBLIC_KEY"),
    "RECAPTCHA_PRIVATE_KEY": os.environ.get("RECAPTCHA_PRIVATE_KEY"),
    "RECAPTCHA_PARAMETERS": {"hl": "en", "render": "explicit"},
    "RECAPTCHA_DATA_ATTRS": {"theme": "dark"},
}

emails_log_file = open(os.path.join(__location__, "../logs/emails.log"), "a+")
