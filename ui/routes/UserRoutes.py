from numpy.lib.user_array import container

from ui.WebUI import WebUI
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from ui.LoginUI import LoginUI
from logic.User import User
from data.Database import Database


class UserRoutes:
    # Retrieve the app instance from WebUI
    __app = WebUI.get_app()


    @staticmethod
    @__app.route("/login")
    def login():
        if "user" in session:
            return redirect((url_for("do_list")))

        # render the login html
        return render_template("login.html")

    # login.html points here to "do_login", successful login leads to homepage
    @staticmethod
    @__app.route("/do_login", methods=["GET", "POST"])
    def do_login():
        """
        Validates user credentials, matches them with database records,
        and redirects based on user role.
        """

        if "user" in session:
            return redirect((url_for("do_list")))

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

        return render_template("confirmation.html")

    @staticmethod
    @__app.route("/register")
    def register():
        if "user" in session:
            return redirect((url_for("do_list")))
        return render_template("register.html")

    @staticmethod
    @__app.route("/do_register", methods=["POST"])
    def do_register():
        if "user" in session:
            return redirect((url_for("do_list")))
        from ui.RegisterUI import RegisterUI

        session['action'] = 'register'

        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        registration_creds = (name, username, email, password, password_confirm)

        register_ui = RegisterUI()
        error = register_ui.confirm_registration(registration_creds)

        if error:
            error_message, error_field = error
            return render_template(
                "register.html",
                error_message=error_message,
                error_field=error_field,
                name=name,
                username=username,
                email=email,
            )

        # After sending the email and generating the code, render the confirmation page
        return render_template("confirmation.html")

    @staticmethod
    @__app.route("/do_confirmation", methods=["POST"])
    def do_confirmation():
        if "user" in session:
            return redirect((url_for("do_list")))

        user_code = request.form.get("confirmation_code")

        # Check if the entered code matches the one in the session
        if user_code and int(user_code) == session.get('confirmation_code'):
            if session.get('action') == 'register':
                # Proceed with final registration
                name = session.get('name')
                username = session.get('username')
                email = session.get('email')
                password = session.get('password')

                # Check if the user already exists in the database
                if Database.check_user(username, email):
                    # Add the user to the database
                    User.add_user(username, password, name, email)

                    # Clear the session after successful registration
                    session.clear()


                    # Redirect to login page after successful registration
                    return redirect(url_for('login'))
                else:
                    return render_template("error.html", message_header="Registration Error",
                                           message_body="Username or Email already exists.")
            # elif session.get("action") == "reset":
            #     return render_template("user/reset_password.html")
            else:
                session.pop('confirmation_code', None)
                session.pop('action', None)

                # Store the user information in the session
                user = User.fetch_user_object(session.get('user_id'))
                session['user'] = user  # Store user_id in the session
                return render_template("do_list.html")
        else:
            # If the code is incorrect, show an error
            return render_template("error.html", message_header="Invalid Code",
                                   message_body="The code you entered is incorrect. Please try again.")

    @staticmethod
    @__app.route("/logout")
    def logout():
        """
        Log out the user
        :return: redirection to homepage
        """
        if "user" in session:
            WebUI.logout()
            del session["user"]
        return redirect(url_for("login"))

    @staticmethod
    @__app.route("/do_list")
    def do_list():
        if "user" not in session:
            return redirect((url_for("login")))
        return render_template("do_list.html")

    @staticmethod
    @__app.route('/save-message', methods=['POST'])
    def save_message():
        try:
            check = 0
            data = request.json
            message_id = data.get("id")
            text = data.get("text")
            container_id = data.get("containerId")

            print("message_id: ", message_id)
            print("text: ", text)
            print("container_id: ", container_id)

            if not message_id or not text:
                return jsonify({"error": "Invalid data"}), 400

            if container_id is "container-1":
                check = 1
            if container_id is "container-2":
                check = 2
            if container_id is "container-3":
                check = 3

            print("check: ", check)
            print(container_id)

            success = Database.save_message(message_id, text, session["user"], check)

            if success:
                return jsonify({"message": "Saved successfully"}), 200
            else:
                return jsonify({"error": "Failed to save message"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500
