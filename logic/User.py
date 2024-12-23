import bcrypt

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
    def pass_validation(password):
        """
        Checks if the password is valid
        :param password: str
        :return: true if valid, false if not
        """
        length_check = len(password) >= 5
        number_check = re.search(r'\d', password)
        special_check = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        return length_check and number_check and special_check

    @staticmethod
    def hash_password(password):
        # Create a salt and hash the password
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        return hashed_password

    @staticmethod
    def fetch_user(user_or_email, password, is_email):
        from data.Database import Database

        return Database.fetch_user(user_or_email, password, is_email)

    @staticmethod
    def fetch_user_object(user_id):
        from data.Database import Database

        return Database.fetch_user_object(user_id)

    @staticmethod
    def add_user(username, hashed_password, name, email):
        """
        Calls the Database method to register a new user
        :param username: str - Username for the new user
        :param hashed_password: bytes - Hashed password for the new user
        :param name: str - Name of the user
        :param email: str - Email of the user
        :return: True if registration is successful, False otherwise
        """
        return Database.add_user(username, hashed_password, name, email)

    def set_userID(self, UserID):
        self.__UserID = UserID

    def set_username(self, Username):
        self.__Username = Username

    def set_password(self, Password):
        self.__Password = Password

    def set_name(self, Name):
        self.__Name = Name

    def set_email(self, email):
        self.__Email = email


