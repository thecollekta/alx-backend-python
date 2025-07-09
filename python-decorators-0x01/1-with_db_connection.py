import functools
import sqlite3


def with_db_connection(func):
    """
    Decorator to handle database connection lifecycle.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None  # Initialize to None
        try:
            # Create the database connection
            conn = sqlite3.connect("users.db")
            result = func(conn, *args, **kwargs)
            return result

        finally:
            # Cleanup: If the connection was successfully created, close it.
            if conn:
                conn.close()

    return wrapper


def setup_database():
    """Create the database and users table for testing"""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    """)
    # Insert data
    cursor.execute(
        "INSERT OR IGNORE INTO users (id, name, email) VALUES ("
        "1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com'"
        ")"
    )
    conn.commit()
    conn.close()


@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
    #### Fetch user by ID with automatic connection handling


setup_database()  # Create DB with data
user = get_user_by_id(user_id=1)
print(user)
