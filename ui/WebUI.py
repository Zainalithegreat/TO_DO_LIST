from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from logic.UserState import UserState

import os
import bcrypt

class WebUI:
    __app = Flask(__name__)

    __app.config["SESSION_FILE_DIR"] = "/flask_session"

    ALLOWED_PATHS = [
        "/",
        "/login",
        "/do_login",
        "/static/web_ui.css",
        "/register",
        "/do_register",
        "/do_confirmation"
    ]

    @classmethod
    def get_app(cls):
        return cls.__app

    # Determine if a user is logged in
    @classmethod
    def get_user(cls):
        if "user" in session:
            return session["user"]
        return None

    @staticmethod
    @__app.before_request
    def before_request():
        """
        Called before each request to check if the user is logged in, if not it redirects to the homepage
        :return: homepage if not logged in
        """
        if "user" not in session:
            if request.path not in WebUI.ALLOWED_PATHS:
                return redirect(url_for('homepage'))
            return
        # Get user state
        user_state = UserState.lookup(WebUI.get_user_key())
        # Create new user state is user_state is none
        if user_state is None:
            UserState(WebUI.get_user())

    @classmethod
    def get_user_key(cls):
        """
        Returns the user key for the current user, if no user it returns none
        """
        user = session["user"]
        if user is None:
            return None
        else:
            try:
                return user.getKey()
            except AttributeError:
                return None