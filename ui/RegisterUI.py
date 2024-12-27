from flask import session
import random
from logic.Email import Email
from logic.User import User


class RegisterUI:
    @staticmethod
    def send_confirmation_code(user_id, email):
        """
        Generates a confirmation code, sends it via email, and stores it in the session
        """
        code = random.randint(10000, 99999)
        email_instance = Email(user_id)
        employee_email = "cis234atesting@gmail.com"
        subject = "Confirmation Code"
        message = f"This is a confirmation code. Please don't share it with anyone: {code}"

        # Send email
        email_instance.send_email(subject, message, email, employee_email)

        # For web users, store the confirmation code in the session
        session['confirmation_code'] = code

        return code

    @staticmethod
    def confirm_registration(web_info):
        name, username, email, password, password_confirm = web_info

        if not name:
            return "Please enter your name.", "name"
        if not username:
            return "Please enter your username.", "username"
        if not email:
            return "Please enter your email.", "email"
        if not password:
            return "Please enter your password.", "password"
        if not password_confirm:
            return "Please confirm your password.", "password_confirm"

        if not User.email_validation(email):
            return "Please enter a valid email address.", "email"
        if not User.pass_validation(password):
            return "Password must be minimum 5 Characters, 1 Number, 1 Special character", "password"
        if password != password_confirm:
            return "Passwords do not match.", "password_confirm"

        user_instance = User(username, password)
        user_id = user_instance.get_user_id()
        code = RegisterUI.send_confirmation_code(user_id, email)
        session['confirmation_code'] = code

        hashed_password = User.hash_password(password)
        session['name'] = name
        session['username'] = username
        session['email'] = email
        session['password'] = hashed_password