from data.Database import Database
import re

class User:
    # __UserID = 0
    __username = ""
    __password = ""


    def __init__(self, username, password=None):
        self.__username = username
        self.__password = password

    def get_user_id(self):
        user_id = Database.get_user_id(self.__username)
        return user_id

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password

    def get_name(self):
        name = Database.get_name(self.__username)
        return name

    def get_email(self):
        email = Database.get_email(self.__username)
        return email

    def get_user_key(self):
        return self.__username.lower()

    @staticmethod
    def email_validation(email):
        """
        Checks if the email is valid, or validates that teh passed string is an email
        :param email: str
        :return: true for valid, false if not
        """

        # Pattern found at https://www.mailercheck.com/articles/email-validation-using-python
        pattern = r"^(?!\.)(?!.*\.\.)[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def fetch_user(user_or_email, password, is_email):
        from data.Database import Database
