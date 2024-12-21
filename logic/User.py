from data.Database import Database

class User:
    # __UserID = 0
    __Username = ""
    __Password = ""


    def __init__(self, Username, Password=None):
        self.__Username = Username
        self.__Password = Password

    def getUserID(self):
        user_id = Database.get_user_id(self.__Username)
        return user_id

    def getUsername(self):
        return self.__Username

    def getPassword(self):
        return self.__Password

    def getName(self):
        name = Database.get_name(self.__Username)
        return name

    def getEmail(self):
        email = Database.get_email(self.__Username)
        return email

    def getKey(self):
        return self.__Username.lower()
