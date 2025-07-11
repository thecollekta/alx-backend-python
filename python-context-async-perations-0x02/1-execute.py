import sqlite3


class ExecuteQuery:
    """
    A context manager that connects to a database, executes a
    query, and provides the results.
    """

    def __init__(self, db_name, query, params=()):
        self.db_name = db_name
        self.query = query
        self.params = params
        self.conn = None

    def __enter__(self):
        """Connects, executes the query, and returns the results."""
        self.conn = sqlite3.connect(self.db_name)
        cursor = self.conn.cursor()
        cursor.execute(self.query, self.params)
        results = cursor.fetchall()
        return results

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleans up by closing the database connection."""
        if self.conn:
            self.conn.close()


query = "SELECT * FROM users WHERE age > ?"
age_param = (25,)
with ExecuteQuery("users.db", query, age_param) as users:
    print(users)
