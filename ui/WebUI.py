from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session

from logic.User import User
from logic.UserState import UserState
import ui.routes
import os
import bcrypt


class WebUI:
    __app = Flask(__name__)

    __app.config["SESSION_FILE_DIR"] = "/flask_session"

    ALLOWED_PATHS = [
        "/",
        "/login",
        "/do_list",
        "/before_list",
        "/update-message",
        "/do_login",
        "/static/web_ui.css",
        "/register",
        "/do_register",
        "/username",
        "/user_do_reset_password",
        "/do_reset_password",
        "/reset_password",
        "/do_confirmation",
        "/save-message",
        "/get-new-message-id",
        "/delete_message"

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
        if "user" in session:
            return redirect((url_for("do_list")))
        return render_template("homepage.html")

    @classmethod
    def run(cls):
        # Causes routes to be added to the app object when the application starts
        from ui.routes.UserRoutes import UserRoutes

        # Identifies web server session
        cls.__app.secret_key = bcrypt.gensalt()
        # Stores session in session files
        cls.__app.config["SESSION_TYPE"] = "filesystem"
        # Constructs new session object which handles requests to the Flask app
        Session(cls.__app)

        # WSGI server handles the app startup in PythonAnywhere
        return cls.__app
