# TODO: replace with psycopg2 imports
import mysql.connector
from mysql.connector import errorcode


class Postgres_Wrapper(object):
    def __init__(self, host, database, user, password):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.logger = logger
        self.config = {
            'user': self.user,
            'password': self.password,
            'host': self.host,
            'database': self.database,
            'raise_on_warnings': True,
            'buffered': True,
            'use_unicode': True
        }
        self.connection = self.connect(**self.config)
        self.analytics = dict()

    def __enter__(self):
        '''
        Context manager enter. Allows class to be used with the "with" keyword
        :return: self
        '''
        if self.connection.autocommit:
            self.connection.autocommit = False
        return self.connection.cursor()

    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Context manager exit. Allows for safe exit from connection. Ensures cursor and db
        connection close if/when script exits.
        :param exc_type: Exception type.
        :param exc_val: Exception value.
        :param exc_tb: Exception Table.
        :return: None
        '''
        if exc_type:
            self.logger.exception(
                "MySQL Error: " + str(exc_type) + "\nTable: " + str(exc_tb) + "\nMessage: " + str(exc_val))
            self.close()
        else:
            self.connection.commit()

    def close(self):
        '''
        Checks if there is an active cursor and connection and closes them.
        :return:
        '''
        if hasattr(self, "cursor"):
            self.cursor.close()
        if hasattr(self, "connection"):
            self.connection.rollback()
            self.connection.close()

    def connect(self, **new_config):
        '''
        If there is an existing connection rollback any uncommitted queries and create a new connection.
        :param new_config: mysql.connector parameters. Reference documentation for long list.
        :return: The mysql connection
        '''
        self.close()
        return mysql.connector.connect(**new_config)

    def execute(self, query):
        # Timer
        return None