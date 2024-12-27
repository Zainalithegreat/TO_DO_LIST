from numpy.lib.user_array import container
from requests import Session
import uuid

from ui.WebUI import WebUI
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from ui.LoginUI import LoginUI
from logic.User import User
from data.Database import Database
import time

TIME_LIMIT = 600
TIME_MINUTES = TIME_LIMIT / 60


#Users routes
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

        session["time"] = time.time()

        return render_template("confirmation.html", time=TIME_MINUTES)

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
        session["time"] = time.time()
        # After sending the email and generating the code, render the confirmation page
        return render_template("confirmation.html", time=TIME_MINUTES)

    @staticmethod
    @__app.route("/reset_password")
    def reset_password():
        if "user" in session:
            return redirect((url_for("do_list")))
        return render_template("username.html")

    @staticmethod
    @__app.route("/user_do_reset_password", methods=["POST"])
    def user_do_reset_password():
        from ui.RegisterUI import RegisterUI
        if "user" in session:
            return redirect((url_for("do_list")))

        session["action"] = "reset"

        user_input = request.form.get("username")
        email = User.email_validation(user_input)
        if email:  # Input is an email
            user_id = User.get_userid_email(user_input)

            user_email = user_input
            session["reset_email"] = user_email
            user_id = user_id[0][0]
            session["user_id"] = user_id
        else:
            user_instance = User(user_input)
            user_id = user_instance.get_user_id()
            user_email = user_instance.get_email()
            session["reset_email"] = user_email
            session["user_id"] = user_id

        register_instance = RegisterUI()
        register_instance.send_confirmation_code(user_id, user_email)

        session["time"] = time.time()
        return render_template("confirmation.html", time=TIME_MINUTES)

    @staticmethod
    @__app.route("/do_reset_password", methods=["POST"])
    def do_reset_password():

        if "user" in session:
            return redirect((url_for("do_list")))

        # Get form data
        password = request.form.get("password")
        confirm_password = request.form.get("password_confirm")

        # Check for missing fields
        if not password or not confirm_password:
            flash("Both password fields are required.", "error")
            return redirect(url_for('do_reset_password'))

        # Password validation
        if not User.pass_validation(password):
            return render_template( "reset_password.html",
                error="Password must be at least 5 characters long, contain a number, and a special character.",
            )

        # Check if passwords match
        if password != confirm_password:
            return render_template("reset_password.html",
                                   error="Passwords do not match.")

        # Get user ID from session
        user_id = session.get("user_id")
        if not user_id:
            return render_template("reset_password.html",
                                   error="Session expired or invalid user ID. Please try again.")

        # Hash the password and update it
        hashed_password = User.hash_password(password)
        User.update_password(hashed_password, user_id)

        return redirect(url_for('login'))


    @staticmethod
    @__app.route("/do_confirmation", methods=["POST"])
    def do_confirmation():
        if "user" in session:
            return redirect(url_for("do_list"))

        user_code = request.form.get("confirmation_code")
        confirmation_code = session.get('confirmation_code')
        # Timestamp when the code was created
        code_generation_time = session.get('time')
        time_left = time.time() - code_generation_time
        remaining_time = TIME_LIMIT - time_left

        print("Remain", remaining_time)

        if remaining_time <= 0:
            return render_template(
                "error.html",
                message_header="Session Expired",
                message_body="Session expired. Please request a new confirmation code.",
                logreg='login'
            )

        # Check if the time limit has been exceeded

        if remaining_time <= 0:
            return render_template(
                "error.html",
                message_header="Time is up",
                message_body=f"Your time is up. Please go back to login.",
                logreg='login'
            )

        # Validate the entered code
        try:
            if int(user_code) != confirmation_code:
                return render_template(
                    "confirmation.html",
                    error="The code you entered is incorrect. Please try again."
                )
        except ValueError:
            return render_template(
                "confirmation.html",
                error="Invalid input. Please enter a valid integer."
            )

        # Code is valid; proceed with the action
        if session.get('action') == 'register':
            name = session.get('name')
            username = session.get('username')
            email = session.get('email')
            password = session.get('password')

            # Check if the user already exists in the database
            if Database.check_user(username, email):
                User.add_user(username, password, name, email)

                # Clear session after successful registration
                session.clear()
                return redirect(url_for('login'))
            else:
                return render_template(
                    "error.html",
                    message_header="Registration Error",
                    message_body="Username or Email already exists.",
                    logreg="login"
                )
        elif session.get("action") == "reset":
            return render_template("reset_password.html")
        else:
            session.pop('confirmation_code', None)
            session.pop('action', None)

            # Load user and their data
            user = User.fetch_user_object(session.get('user_id'))
            session['user'] = {"username": user.get_username(), "password": user.get_password()}
            print(session["user"])
            user_instance = User(session["user"]["username"])
            user_id = user_instance.get_user_id()
            container_one = Database.get_messages(user_id, 1)
            container_two = Database.get_messages(user_id, 2)
            container_three = Database.get_messages(user_id, 3)

            return render_template(
                "do_list.html",
                container_one=container_one,
                container_two=container_two,
                container_three=container_three
            )

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
            return redirect(url_for("login"))

        # Reconstruct the User object from session data
        user_instance = User.from_dict(session["user"])
        print(user_instance)

        # Get the user ID
        user_id = user_instance.get_user_id()

        # Fetch messages from the database
        container_one = Database.get_messages(user_id, 1)
        container_two = Database.get_messages(user_id, 2)
        container_three = Database.get_messages(user_id, 3)

        # Render the HTML template with the fetched data
        return render_template(
            "do_list.html",
            container_one=container_one,
            container_two=container_two,
            container_three=container_three
        )

    @staticmethod
    @__app.route('/save-message', methods=['POST'])
    def save_message():
        import time

        try:
            # Extract and validate incoming JSON data
            data = request.json
            message_id = data.get('id')
            text = data.get("text")
            container_id = data.get("containerId")
            print("Messages", message_id)

            if not message_id or not text or not container_id:
                print("Missing fields:", data)  # Log missing fields
                return jsonify({"error": "Missing required fields"}), 400

            container_checks = {
                "container-1": 1,
                "container-2": 2,
                "container-3": 3,
            }
            check = container_checks.get(container_id)
            if check is None:
                return jsonify({"error": "Invalid container ID"}), 400

            print("Received data:", data)

            user_instance = User(session["user"]["username"])
            user_id = user_instance.get_user_id()

            print("Message_id: ", message_id)
            if Database.check_message_box(user_id, message_id):
                Database.update_message_box(text, message_id, user_id)
                return jsonify({"message": "Saved successfully"}), 200

            success = Database.save_message(text, user_id[0], check, message_id)
            if success:
                print("Message saved successfully")
                return jsonify({"message": "Saved successfully"}), 200
            else:
                return jsonify({"error": "Failed to save message"}), 500

        except KeyError as e:
            print(f"KeyError: {e}")
            return jsonify({"error": f"Missing key: {str(e)}"}), 400
        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    @staticmethod
    @__app.route("/update-message", methods=['POST'])
    def update_message():
        try:
            data = request.json
            container_id = data.get("new_container")
            message_id = data.get("textarea_id")
            check = 0

            print("containerID", container_id)

            if container_id == "container-1":
                check = 1
            elif container_id == "container-2":
                check = 2
            elif container_id == "container-3":
                check = 3

            print("check: ", check)

            print("message_id: ", message_id)

            user_instance = User(session["user"]["username"])
            user_id = user_instance.get_user_id()

            success = Database.update_message(message_id, check, user_id[0])

            if success:
                return jsonify({"message": "Saved successfully"}), 200
            else:
                return jsonify({"error": "Failed to save message"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @__app.route('/get-new-message-id', methods=['GET'])
    def get_new_message_id():
        try:
            new_message_id = str(uuid.uuid4())
            print("Message_ID", new_message_id)

            return jsonify({"newMessageId": new_message_id}), 200
        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500


    @staticmethod
    @__app.route("/delete_message", methods=["POST"])
    def delete_message():
        try:
            data = request.json
            id = data.get("id")

            print("Id:", id)

            if not id:
                return jsonify({"error": "Message ID is required"}), 400
            success = Database.delete_message(id)
            if success:
                print("success")
                return jsonify({"message": "Message deleted successfully"}), 200
            else:
                print("unsuccess")
                return jsonify({"error": "Message did not delete"}), 500

        except Exception as e:
            print("Error during message deletion:", str(e))
            return jsonify({"error": "Internal server error"}), 500
















