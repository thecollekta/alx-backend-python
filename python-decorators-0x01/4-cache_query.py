import functools
import sqlite3
import time


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


query_cache = {}


def cache_query(func):
    """
    Decorator that caches the results of a database query.
    """

    @functools.wraps(func)
    def wrapper(conn, query):
        current_time = time.time()

        # Check for query existence in cache and not expired
        if query in query_cache:
            result, timestamp = query_cache[query]
            if current_time - timestamp < 10:
                print("Returning results from cache.")
                return result
        else:
            print("Querying database and caching result.")

        # If not present in cache/expired, execute query and cache result
        result = func(conn, query)

        # Store new result in the cache
        query_cache[query] = (result, current_time)
        print("Cached new result.")
        return result

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
    return cursor.fetchone()  #### Fetch user by ID with automatic connection handling


# Setup and test
setup_database()  # Create DB with data
user = get_user_by_id(user_id=1)
print(user)


@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


#### First call will cache the result
print("\nFirst call:")
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

#### Second call will use the cached result
print("\nSecond call:")
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

#### Cache expiration and calling again
print("\nWaiting 11 seconds...")
time.sleep(11)
print("Third call (after expiration):")
users_expired = fetch_users_with_cache(query="SELECT * FROM users")
print(users_expired)
