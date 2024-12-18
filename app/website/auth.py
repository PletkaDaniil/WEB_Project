from flask import Blueprint, render_template, redirect, url_for, request, flash, session, abort
from .models import User
from . import db, mail
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
import os
import pathlib
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import requests
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_mail import Message
import random
import json

auth = Blueprint("auth", __name__)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

with open(client_secrets_file, "r") as f:
    client_data = json.load(f)

GOOGLE_CLIENT_ID = client_data['web']['client_id']
GOOGLE_CLIENT_SECRET = client_data['web']['client_secret']
REDIRECT_URI = client_data['web']['redirect_uris'][0]

flow = Flow.from_client_config(
    {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uris": [REDIRECT_URI],
            "auth_uri": client_data['web']['auth_uri'],
            "token_uri": client_data['web']['token_uri'],
            "auth_provider_x509_cert_url": client_data['web']['auth_provider_x509_cert_url'],
        }
    },
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri=REDIRECT_URI
)

def is_email_valid(email):
    email_regex = r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
    return re.match(email_regex, email) is not None

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.home"))
            else:
                flash("Password is incorrect.", category="error")
        else:
            flash("Email doesn't exist.", category="error")

    return render_template("login.html", user=current_user)

@auth.route("/login/google")
def login_google():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@auth.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID,
        clock_skew_in_seconds=10
    )

    email = id_info.get("email")
    name = id_info.get("name")
    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(
            email=email,
            username=name,
            password=generate_password_hash("auth11111go"+email+"canwe", method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=True)
    else:
        login_user(user, remember=True)

    return redirect(url_for("views.home"))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        first_password = request.form.get("password1")
        second_password = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash("Email is already in use.", category="error")
        elif username_exists:
            flash("Username is already in use.", category="error")
        elif first_password != second_password:
            flash("Passwords don't match.", category="error")
        elif len(username) <= 2:
            flash("Username is too short.", category="error")
        elif len(first_password) < 6:
            flash("Password is too short.", category="error")
        elif not is_email_valid(email):
            flash("Invalid email address. Please enter a valid email.", category="error")
        else:
            confirmation_code = random.randint(100000, 999999)
            session["confirmation_code"] = confirmation_code
            session["pending_user"] = {
                "email": email,
                "username": username,
                "password": generate_password_hash(first_password, method='pbkdf2:sha256')
            }
            
            msg = Message(
                subject="Email Confirmation Code",
                sender="your_email@gmail.com",
                recipients=[email]
            )
            msg.body = f"Your confirmation code is: {confirmation_code}"
            mail.send(msg)

            flash("Confirmation code sent to your email. Please check your inbox.", category="info")
            return redirect(url_for("auth.confirm_email"))

    return render_template("sign_up.html", user=current_user)


@auth.route("/confirm-email", methods=["GET", "POST"])
def confirm_email():
    if request.method == "POST":
        entered_code = request.form.get("confirmation_code")
        if str(session.get("confirmation_code")) == entered_code:
            pending_user = session.get("pending_user")
            if pending_user:
                new_user = User(
                    email=pending_user["email"],
                    username=pending_user["username"],
                    password=pending_user["password"]
                )
                db.session.add(new_user)
                db.session.commit()
                session.pop("confirmation_code", None)
                session.pop("pending_user", None)
                flash("Email confirmed and user created!", category="success")
                login_user(new_user, remember=True)
                return redirect(url_for("views.home"))
        else:
            flash("Invalid confirmation code. Please try again.", category="error")

    return render_template("confirm_email.html", user=current_user)