import functools
import sqlite3
import datetime from datetime


def log_queries(func):
    """
    A decorator to log the SQL query before executing it.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Handle both positional and keyword arguments
        query = args[0] if args else kwargs.get("query", "No query provided")
        current_time = datetime.now()
        print(f"[{current_time}]Executing SQL Query: {query}")
        result = func(*args, **kwargs)
        return result

    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")
