from sqlite3 import Cursor

from mysql.connector.abstracts import MySQLCursorAbstract


def cursor_wrapper(connection):
    """
    Returns the appropriate cursor wrapper based on the type of the database connection.

    Args:
        connection: The database connection object.

    Returns:
        A cursor object that is either a MySQL cursor or a wrapped SQLite cursor.
    """
    if isinstance(connection.cursor(), MySQLCursorAbstract):
        return connection.cursor()
    else:
        return Sqlite3CursorWrapper(connection)


class Sqlite3CursorWrapper(Cursor):
    """
    A wrapper class for the SQLite3 Cursor to handle query parameter replacement.
    """

    def __init__(self, connection):
        """
        Initializes the sqlite3_cursor_wrapper with a database connection.

        Args:
            connection: The SQLite3 database connection object.
        """
        super().__init__(connection)

    def execute(self, query: str, params=None):
        """
        Executes a SQL query after replacing the parameter placeholders.

        Args:
            query (str): The SQL query to be executed.
            params (tuple, optional): The parameters to be used in the SQL query.

        Returns:
            The result of the query execution.
        """
        query = self._replace_query(query)
        return super().execute(query, params)

    def _replace_query(self, query: str):
        """
        Replaces MySQL-style placeholders with SQLite3-style placeholders.

        Args:
            query (str): The SQL query with MySQL-style placeholders.

        Returns:
            str: The SQL query with SQLite3-style placeholders.
        """
        return query.replace('%s', '?').replace('%i', '?').replace('%f', '?').replace('%d', '?')

