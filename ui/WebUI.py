from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session

from logic.User import User
from logic.UserState import UserState
import ui.routes
import os
import bcrypt


class WebUI:
    __app = Flask(__name__)
    __app.secret_key = os.urandom(24)

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

    import os
    from flask import Flask, session
    from flask_session import Session
    import bcrypt

    class MyApp:
        __app = Flask(__name__)

        @classmethod
        def run(cls):
            # Import routes after app initialization
            from ui.routes.UserRoutes import UserRoutes

            # Determine the configuration folder based on environment
            if "APPDATA" in os.environ:
                path = os.environ["APPDATA"]
            elif "HOME" in os.environ:
                path = os.environ["HOME"]
            else:
                raise Exception("Couldn't find config folder.")

            # Set the secret key (ensure it's unique and random for security)

            # Configure Flask session handling
            cls.__app.config["SESSION_TYPE"] = "filesystem"  # Use filesystem to store session data
            Session(cls.__app)  # Initialize session

            # For PythonAnywhere, we don't need to specify SSL context, so we just use:
            cls.__app.run(debug=True, host="0.0.0.0", port=8080)

    if __name__ == '__main__':
        MyApp.run()
