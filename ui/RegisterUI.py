from flask import session
import random
from logic.Email import Email


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
