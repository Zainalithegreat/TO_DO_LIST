from ui.WebUI import WebUI
from ui.LoginUI import LoginUI
from flask import render_template, request, session, redirect, url_for, flash
from logic.User import User
from data.Database import Database

class UserRoutes:
    __app = WebUI.get_app()

    @staticmethod
    @__app.route("/login")
    def login():
        return render_template("login.html")

    @staticmethod
    @__app.route("/do_login", methods=["GET", "POST"])
    def do_login():
        """
        Validates user credentials, matches them with database records,
        and redirects based on user role.
        """

        session['action'] = 'login'

        user_or_email = request.form.get("username")
        password = request.form.get("password")

        login_creds = (user_or_email, password)

        login_ui = LoginUI()
        error = login_ui.user_login(login_creds)

        if error:
            error_message = error
            return render_template(
                "login.html",
                error_message=error_message
            )

        return render_template("onfirmation.html")




      