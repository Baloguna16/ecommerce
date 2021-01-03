import os
import json
import requests

from flask_login import LoginManager
from oauthlib.oauth2 import WebApplicationClient

from support.config import GoogleOAuth

login_manager = LoginManager()

oauth = GoogleOAuth()
client = WebApplicationClient(oauth.GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(oauth.GOOGLE_DISCOVERY_URL).json()
