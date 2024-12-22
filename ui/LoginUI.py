from flask import session

from logic.User import User
import time


class LoginUI:
    @staticmethod
    def user_login(login):
        user, password = login
        if not user or not password:
            return "Please enter both username and password."

        email = User.email_validation(user)

        result = User.fetch_user(user, password, is_email=email)

        if not result:
            return "Invalid username or password."
        else:
            time_limit = 600
            time_minutes = time_limit / 60
            time = "Time", f"You have {int(time_minutes)} minutes remaining until the code is invalid"
            # Fetch the full user object
            user = User.fetch_user_object(result)

            # Use user information
            user_id = user.getUserID()
            user_email = user.getEmail()

            code = RegisterUI.send_confirmation_code(user_id, user_email)
            start_time = time.time()

            # Store the code in the session for web users
            if platform == "web":
                session['confirmation_code'] = code
                session['user_id'] = user_id
                return

            while True:
                time_left = time.time() - start_time
                remaining_time = time_limit - time_left
                if remaining_time <= 0:
                    break
                else:
                    try:
                        user_input = simpledialog.askstring("Input Required", "Confirmation Code:")
                        if user_input is None:
                            return
                        if int(user_input) != code:
                            messagebox.showerror("Invalid", "Please enter the correct confirmation code.")
                        else:
                            print(user_input)
                            break
                    except ValueError:
                        messagebox.showerror("Invalid", "Invalid input. Please enter a valid integer.")

            time_left = time.time() - start_time
            remaining_time = time_limit - time_left

            if remaining_time <= 0:
                messagebox.showinfo("Time up", "Time is up please try again")

            elif remaining_time > 0:
                messagebox.showinfo("Successful Login", "Successful Login")
                print(user_id)

