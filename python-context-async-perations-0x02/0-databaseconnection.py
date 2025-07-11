import sqlite3


class DatabaseConnection:
    """A context manager to handle SQLite database connections."""

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        """Called when entering the 'with' block."""
        print(f"Setting up the resource: Connecting to {self.db_name}")
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Called when exiting the 'with' block."""
        print("Tearing down resource: Closing the connection.")
        if self.conn:
            self.conn.close()


with DatabaseConnection("users.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    results = cursor.fetchall()
    print(results)
