class UserState:
    __user = None
    __map = {}

    # retrieves the user details from the database, tied to this user's session
    # put whatever we need to retrieve in here
    def __init__(self, user):
        from data.Database import Database

        self.__user = user
        # key is used to identify the user and refer to them in a unique way
        self.__class__.__map[self.get_key()] = self

    @classmethod
    def logout(cls, user_key):
        if user_key in cls.__map:
            del cls.__map[user_key]

    def get_key(self):
        return self.__user.get_user_key()

    @classmethod
    def lookup(cls, key):
        """
        search the map for the passed in user key
        :return: the map key if found, else None
        """
        if key in cls.__map:
            return cls.__map[key]
        else:
            return None
