import uuid

from ui.WebUI import WebUI
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from ui.LoginUI import LoginUI
from logic.User import User
from data.Database import Database
import time



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

                user_instance = User(session["user"].get_username())
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
        user_instance = User(session["user"].get_username())
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
    @__app.route('/save-message', methods=['POST'])
    def save_message():
        import time
        time.sleep(1)  # Simulating delay for testing

        try:
            # Extract and validate incoming JSON data
            data = request.json
            message_id = data.get('id')
            text = data.get("text")
            container_id = data.get("containerId")
            print("Messages", message_id)
            time.sleep(1)

            if not message_id or not text or not container_id:
                print("Missing fields:", data)  # Log missing fields
                return jsonify({"error": "Missing required fields"}), 400

            # Determine the check value based on container_id
            container_checks = {
                "container-1": 1,
                "container-2": 2,
                "container-3": 3,
            }
            check = container_checks.get(container_id)
            if check is None:
                return jsonify({"error": "Invalid container ID"}), 400

            print("Received data:", data)
            time.sleep(1)

            # Fetch user ID from the session
            user_instance = User(session["user"].get_username())
            user_id = user_instance.get_user_id()

            print("Message_id: ", message_id)
            if Database.check_message_box(user_id, message_id):
                Database.update_message_box(text, message_id, user_id)
                return jsonify({"message": "Saved successfully"}), 200

            # Save the message in the database
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

            user_instance = User(session["user"].get_username())
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
            # Get the current maximum message ID from the database
            new_message_id = str(uuid.uuid4())
            print("Message_ID", new_message_id)

            return jsonify({"newMessageId": new_message_id}), 200
        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    from flask import request, jsonify

    @staticmethod
    @__app.route("/delete_message", methods=["POST"])
    def delete_message():
        try:
            # Parse the incoming JSON request
            data = request.json
            id = data.get("id")

            # Debugging: Print the ID to the console
            print("Id:", id)

            # Validate that the ID is provided
            if not id:
                return jsonify({"error": "Message ID is required"}), 400

            # Perform the deletion using the Database helper
            success = Database.delete_message(id)

            # Check if deletion was successful
            if success:
                print("success")
                return jsonify({"message": "Message deleted successfully"}), 200
            else:
                print("unsuccess")
                return jsonify({"error": "Message did not delete"}), 500

        except Exception as e:
            # Catch and log unexpected errors
            print("Error during message deletion:", str(e))
            return jsonify({"error": "Internal server error"}), 500
















