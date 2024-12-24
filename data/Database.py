import pymssql
import logging
import bcrypt

# Set up logging configuration (this could be set up elsewhere in your application)
logging.basicConfig(level=logging.INFO)


class Database:
    __connection = None

    @classmethod
    def connect(cls):
        # the connection variables
        if cls.__connection is None:
            try:
                cls.__connection = pymssql.connect(
                    server="localhost",
                    database="List"
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
                      SELECT  UserID, 1, Email, Password
                      FROM Users
                      WHERE Email = %s;
                      """
        else:
            sql = """
                      SELECT  UserID, Username, Email, Password
                      FROM Users
                      WHERE Username = %s;
                      """

        cursor = cls.get_cursor()
        cursor.execute(sql, (user_or_email,))
        result = cursor.fetchone()
        print("result", result)

        if result and cls.check_password(result[3], password):
            return result[0]
        else:
            return None

    @classmethod
    def check_password(cls, stored_password, provided_password):
        if isinstance(stored_password, str):
            stored_password = stored_password.encode('utf-8')
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)


    @classmethod
    def fetch_user_object(cls, user_id):
        """
        Method to fetch a user object from the database.
        :param user_id: user_id, str
        :return: user object, if valid credentials
        """
        from logic.User import User
        sql = """
                   SELECT UserID, Username, Password, Name, Email
                   FROM Users
                   WHERE UserID = %s;
                 """

        cursor = cls.get_cursor()
        cursor.execute(sql, user_id)
        result = cursor.fetchone()

        if result:
            user = User(result[1], result[2])
            user.set_userID(result[0])
            user.set_name(result[3])
            user.set_email(result[4])
            return user
        else:
            return None

    @classmethod
    def add_user(cls, username, hashed_password, name, email):
        """
        Adds a new user into the Users table
        :param username: str - Username for the new user
        :param hashed_password: bytes - Hashed and salted password
        :param name: str - Name of the user
        :param email: str - Email of the user
        :param role: str - Role of the user, default is 'Subscriber'
        :return: True if registration is successful, False otherwise
        """
        sql = """
            INSERT INTO Users (Username, Password, Name, Email)
            VALUES (%s, %s, %s, %s)
        """

        cursor = None
        try:
            # Create a cursor and execute the insert query
            cursor = cls.get_cursor()

            # Execute the query
            cursor.execute(sql, (username, hashed_password, name, email))

            # Commit the changes to the database
            cls.__connection.commit()

            # Log success
            logging.info(f"User '{username}' created successfully.")

            return True
        except pymssql.DatabaseError as e:
            # Log the error
            logging.error(f"Error adding user: {str(e)}")

            # Rollback any changes in case of error
            cls.__connection.rollback()

            return False
        finally:
            # Ensure cursor and connection are closed
            if cursor:
                cursor.close()
            cls.close_connection()

    @classmethod
    def check_user(cls, username, email):
        sql = """
                   SELECT * 
                   FROM Users 
                   WHERE Username = %s OR Email = %s
               """
        cursor = cls.get_cursor()
        cursor.execute(sql, (username, email))
        print("WE get here so something wrong in userid")
        if cursor.fetchone():  # If a record is found, return False
            print("Username or email already exists.")
            return False
        else:
            print("No users")
            return True

    @classmethod
    def save_message(cls, text, user_id, checked, message_var):
        try:

            # Updated SQL query (escape reserved keywords like `check`)
            sql = """
                INSERT INTO Messages (Message, UserID, Checked, MessageVar)
                VALUES (%s, %s, %s, %s)
            """
            print(f"Executing SQL Query: {sql}")

            cursor = cls.get_cursor()
            cursor.execute(sql, (text, user_id, checked, message_var))
            cls.__connection.commit()
            return True
        except Exception as e:
            print(f"Error saving message: {e}")
            return False

    @classmethod
    def get_messages(cls, user_id, container):
        sql = """
                              SELECT Message, MessageVar
                              FROM   Messages
                              WHERE  UserID = %s AND Checked = %s
                              """

        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id, container))
        result = cursor.fetchall()
        print("result: ", result)
        return result

    @classmethod
    def update_message(cls, message_var, checked, user_id):
        sql = """
        UPDATE Messages
        SET Checked = %s
        WHERE MessageVar = %s AND UserID = %s
        """
        cursor = cls.get_cursor()
        try:
            print("Executing SQL:", sql)
            print("With parameters:", (checked, message_var, user_id))
            cursor.execute(sql, (checked, message_var, user_id))
            cls.__connection.commit()
            print("Message updated successfully")
        except Exception as e:
            print(f"Error executing SQL: {e}")
            cls.__connection.rollback()
        finally:
            if cursor:
                cursor.close()
            cls.close_connection()

    @classmethod
    def check_message(cls, user_id, message):
        sql = """
                          SELECT * 
                          FROM Messages 
                          WHERE UserID = %s AND Message = %s
                      """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id, message))
        result = cursor.fetchall()
        if result:  # If a record is found, return False
            print("A message is found with that user")
            return False
        else:
            print("No message")
            return True

    @classmethod
    def get_message_id(cls):
        sql = """
            SELECT MAX(MessageID) FROM Messages;
        """
        cursor = cls.get_cursor()  # Assuming you have a method to get a database cursor
        cursor.execute(sql)
        result = cursor.fetchone()
        print("The ID is", result)

        # If result is None (i.e., no rows in the table), return 0
        if result and result[0] is not None:
            return result[0]  # Extract the value of the first column
        else:
            result = 0
            return result # Return 0 if no rows found

    @classmethod
    def check_message_box(cls, user_id, message_var):
        sql = """
                                  SELECT * 
                                  FROM Messages 
                                  WHERE UserID = %s AND MessageVar = %s
                              """
        cursor = cls.get_cursor()
        cursor.execute(sql, (user_id, message_var))
        result = cursor.fetchall()
        if result:
            return True
        else:
            return False

    @classmethod
    def update_message_box(cls, message, message_var, user_id,):
        sql = """
               UPDATE Messages
               SET Message = %s
               WHERE MessageVar = %s AND UserID = %s
               """
        cursor = cls.get_cursor()
        cursor.execute(sql, (message, message_var, user_id))
        cls.__connection.commit()
        print("Updated correctly")

