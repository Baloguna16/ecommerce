#Reference: https://realpython.com/flask-google-login/
import os
import json
import requests
#import sqlite3

from flask import Flask, redirect, Blueprint, request, url_for, render_template, flash
from flask_login import current_user, login_required, login_user, logout_user

# Internal imports
#from db import init_db_command
#from user import User
from support.models import User,Cart, db
from support.login import login_manager, oauth, client, get_google_provider_cfg

bp = Blueprint('auth', __name__)

login_manager.login_view = "auth.index"
login_manager.login_message = u"You should login first, bro."

@login_manager.user_loader
def load_user(id):
    user = User.query.get_or_404(id)
    return user

@bp.route("/")
def index():
    return render_template('main/index.html', user=current_user)

@bp.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@bp.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
        )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(oauth.GOOGLE_CLIENT_ID, oauth.GOOGLE_CLIENT_SECRET),
        )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User.query.filter_by(email=users_email).first()
    if not user:
        user = User(name=users_name, email=users_email, unique=unique_id)
        db.session.add(user)
        db.session.commit()

        cart = Cart(owner_id=user.id)
        db.session.add(cart)
        db.session.commit()

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect("/")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")
