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
                return user.get_user_key()
            except AttributeError:
                return None

    @classmethod
    def login(cls, user):
        """
        logs in the passed-in user
        """
        session["user"] = user
        UserState(user)

    @classmethod
    def logout(cls):
        """
        Log out the user
        """
        UserState.logout(WebUI.get_user_key())

    @staticmethod
    @__app.route('/index')
    @__app.route('/index.html')
    @__app.route('/index.php')
    @__app.route('/')
    # render_template(file name): looks up a template in the templates folder
    # Example:
    def homepage():
        return render_template("homepage.html")

    @classmethod
    def run(cls):
        # causes routes to be added to app object on run
        # pycharm says they are unused (greyed out), but it is incorrect, they are needed

        if "APPDATA" in os.environ:
            path = os.environ["APPDATA"]
        elif "HOME" in os.environ:
            path = os.environ["HOME"]
        else:
            raise Exception("Couldn't find config folder.")

        # identifies web server session
        cls.__app.secret_key = bcrypt.gensalt()
        # stores session in session files
        cls.__app.config["SESSION_TYPE"] = "filesystem"
        # constructs new session object which handles requests to the flask app
        Session(cls.__app)
        # paths may need to be adjusted, currently placeholders
        cls.__app.run(host="0.0.0.0", port=8444, ssl_context=(path + "/234A_CommitChaos/cert.pem",
                                                              path + "/234A_CommitChaos/key.pem"))
