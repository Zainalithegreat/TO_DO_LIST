from data.Database import Database

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
