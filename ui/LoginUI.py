from flask import session
from ui.RegisterUI import RegisterUI

from logic.User import User
import time


class LoginUI:
    @staticmethod
    def user_login(login):
        user, password = login
        if not user or not password:
            return "Please enter both username and password."

        email = User.email_validation(user)
        print(email)

        result = User.fetch_user(user, password, is_email=email)
        print(result)
        if not result:
            return "Invalid username or password."
        else:
            user = User.fetch_user_object(result)

            # Use user information
            user_id = user.get_user_id()
            user_email = user.get_email()

            code = RegisterUI.send_confirmation_code(user_id, user_email)
            start_time = time.time()

            print("Code: ", code)

            # Store the code in the session for web users
            session['confirmation_code'] = code
            session['user_id'] = user_id



