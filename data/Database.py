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




