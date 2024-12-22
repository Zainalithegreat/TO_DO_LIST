import pymssql
import bcrypt


class Database:
    __connection = None

    @classmethod
    def connect(cls):
        # the connection variables
        if cls.__connection is None:
            try:
                cls.__connection = pymssql.connect(
                    server="localhost",
                    database="Do_List",
                    trusted=True,
                )
                print(cls.__connection)
            except pymssql.DatabaseError as e:
                print(f"Database connection failed: {e}")
                cls.__connection = None

    @classmethod
    def get_cursor(cls):
        """
        Class to create a cursor for executing queries
        :return: cursor
        """
        if cls.__connection is None:
            cls.connect()
        return cls.__connection.cursor()

    @classmethod
    def close_connection(cls):
        """
        Close the connection to the database
        """
        if cls.__connection:
            cls.__connection.close()
            cls.__connection = None

    @classmethod
    def get_user_id(cls, username):
        sql = """
                       SELECT UserID
                       FROM   Users
                       WHERE  Username = %s
                       """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        # print("result: ", result)
        return result

    @classmethod
    def get_name(cls, username):
        sql = """
                       SELECT Name
                       FROM   Users
                       WHERE  Username = %s
                       """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        print("result: ", result)
        return result

    @classmethod
    def get_email(cls, username):
        sql = """
                       SELECT Email
                       FROM   Users
                       WHERE  Username = %s
                       """

        cursor = cls.get_cursor()
        cursor.execute(sql, (username,))
        result = cursor.fetchone()
        print("result: ", result)
        return result

    @classmethod
    def fetch_user(cls, user_or_email, password, is_email=False):
        """
        Method to fetch a user from the database.
        :param user_or_email: username or email used for login
        :param password: password provided by the user
        :param is_email: flag to check if login is via email
        :return: found user, if valid credentials
        """
        if is_email:
            sql = """
                     SELECT  UserID, 1, Email, Password, Role
                     FROM Users
                     WHERE Email = %s;
                     """
        else:
            sql = """
                     SELECT  UserID, Username, Email, Password, Role
                     FROM Users
                     WHERE Username = %s;
                     """

        cursor = cls.get_cursor()
        cursor.execute(sql, (user_or_email,))
        result = cursor.fetchone()

        if result and cls.check_password(result[3], password):
            return result[0]
        else:
            return None




