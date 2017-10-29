import psycopg2

class pgWrapper(object):
    def __init__(self, database, user, password, host = "localhost"):
        self.connection = self.connect(database, user, password, host)
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
            raise ValueError(exc_type, exc_val)
        else:
            self.connection.commit()

        self.close()

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


    def connect(self, database, user, password, host):
        '''
        If there is an existing connection rollback any uncommitted queries and create a new connection.
        :return: postgres connection
        '''
        self.close()
        connection_string ="dbname=\'"+ database +\
                               "\' user=\'" + user +\
                               "\' host=\'" +  host +\
                               "\' password=\'" + password + "\'"

        return psycopg2.connect(connection_string)

# Example
# with database("testdb", "test", "test") as db:
#     db.execute("SELECT * FROM table1;")
#     print(db.fetchone())
