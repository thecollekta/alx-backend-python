# Python Decorators

## Overview

A collection of Python decorators for database operations, including query logging and automatic connection management. These decorators provide clean, reusable patterns for database interaction functions.

## Features

* **Automatic Query Logging**: Monitor and debug SQL queries before execution
* **Database Connection Management**: Automatic connection lifecycle handling
* **Transaction Management**: Automatic commit/rollback handling for database operations
* **Retry Mechanism**: Automatic retry on failure with configurable attempts and delays
* **Flexible Argument Handling**: Supports both positional and keyword arguments
* **Function Metadata Preservation**: Uses `functools.wraps` to maintain original function properties
* **Non-intrusive**: No modification required to existing database functions
* **Resource Safety**: Proper cleanup with try/finally blocks
* **Query Caching**: Avoid redundant database calls with automatic result caching
* **Time-based Expiration**: Configurable cache expiration time (default: 10 seconds)
* **Efficient Resource Usage**: Reduces database load for repeated queries
* **Transparent Integration**: Works seamlessly with existing database functions

## Installation

No external dependencies required. Only uses Python standard library modules:

```python
import sqlite3
import functools
import time
from datetime import datetime
```

## Decorators

### 1. Log Queries Decorator

A decorator that logs SQL queries before execution, designed for database interaction functions.

#### Implementation

```python
import sqlite3
import functools
from datetime import datetime

def log_queries(func):
    """
    A decorator to log the SQL query before executing it.
  
    Args:
        func: The function to be decorated
      
    Returns:
        wrapper: The decorated function with logging capability
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Handle both positional and keyword arguments
        query = args[0] if args else kwargs.get('query', 'No query provided')
        current_time = datetime.now()
        print(f"[{current_time}]Executing SQL Query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    """Fetch all users from the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
```

#### Usage Example

```python
# Using positional argument
users = fetch_all_users("SELECT * FROM users")

# Using keyword argument
users = fetch_all_users(query="SELECT * FROM users WHERE active = 1")

# Both will output:
# Executing SQL Query: SELECT * FROM users
# Executing SQL Query: SELECT * FROM users WHERE active = 1
```

### 2. Database Connection Decorator

A decorator that automatically handles database connection lifecycle - opening, passing to function, and closing connections.

Implementation:

```python
import sqlite3
import functools

def with_db_connection(func):
    """
    Decorator to handle database connection lifecycle.
    
    Args:
        func: The function to be decorated (must accept conn as first parameter)
        
    Returns:
        wrapper: The decorated function with automatic connection management
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            # Create database connection
            conn = sqlite3.connect('users.db')
            
            # Call original function with connection as first argument
            result = func(conn, *args, **kwargs)
            
            return result
        finally:
            # Ensure connection is closed even if an error occurs
            if conn:
                conn.close()
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    """Get a user by ID with automatic connection handling."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()
```

Usage Example:

```python
# Database setup (run once)
def setup_database():
    """Create the database and users table for testing"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    # Insert data
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')")
    conn.commit()
    conn.close()

# Usage
setup_database()
user = get_user_by_id(user_id=1)
print(user)  # Output: (1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')
```

### 3. Transaction Management Decorator

A decorator that manages database transactions by automatically committing successful operations or rolling back on errors.

Implementation:

```python
def transactional(func):
    """
    Decorator to manage database transactions.

    Args:
        func: The function to be decorated (must accept conn as first parameter)
        
    Returns:
        wrapper: The decorated function with automatic transaction management
    """
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            result = func(conn, *args, **kwargs)
        except Exception as e:
            conn.rollback()
            print("Transaction rolled back due to an error.")
            raise e
        else:
            conn.commit()
            print("Transaction committed successfully.")
        return result
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))
```

Usage Example:

```python
# Update user email with automatic transaction handling
update_user_email(user_id=1, new_email="<kwame.nkrumah@gmail.com>")

# Output on success
# Transaction committed successfully

# Output on error
# Transaction rolled back due to an error
```

### 4. Retry on Failure Decorator

A decorator that automatically retries function calls on failure with configurable retry attempts and delays.

Implementation:

```python
import functools
import time

def retry_on_failure(retries=3, delay=1):
    """
    A decorator that retries a function call on failure.

    Args:
        retries (int): Number of retry attempts (default: 3)
        delay (int): Delay between retries in seconds (default: 1)
        
    Returns:
        decorator: The decorator function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    # Attempt to run function
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"Attempt {attempt + 1}/{retries} failed: {str(e)}")
                    
                    # Don't sleep after the last attempt
                    if attempt < retries - 1:
                        time.sleep(delay)
            
            print("All retries failed.")
            raise last_exception
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    """Fetch users with automatic retry on failure."""
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()
```

Usage Example:

```python
# Fetch users with automatic retry on failure
users = fetch_users_with_retry()
print(users)

# Output on success
# [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]

# Output on failure
# Attempt 1/3 failed: database is locked
# Attempt 2/3 failed: database is locked
# Attempt 3/3 failed: database is locked
# All retries failed
# sqlite3.OperationalError: database is locked
```

Configuration Options

```python
# Default settings (3 retries, 1 second delay)
@retry_on_failure()
def basic_retry_function():
    pass

# Custom settings (5 retries, 2 second delay)
@retry_on_failure(retries=5, delay=2)
def custom_retry_function():
    pass

# Single retry with no delay
@retry_on_failure(retries=1, delay=0)
def single_retry_function():
    pass
```

### 5. Query Caching Decorator

A decorator that caches database query results with time-based expiration to avoid redundant database calls.

Implementation:

```python
import functools
import time

query_cache = {}

def cache_query(func):
    """
    Decorator that caches the results of a database query.
    """
    @functools.wraps(func)
    def wrapper(conn, query):
        current_time = time.time()
        
        # Check if query exists in cache and hasn't expired
        if query in query_cache:
            result, timestamp = query_cache[query]
            if current_time - timestamp < 10:
                print("Returning results from cache.")
                return result
            else:
                print("Cache expired. Querying database again.")
        else:
            print("Querying database and caching result.")
            
        # Execute query and cache result with timestamp
        result = func(conn, query)
        query_cache[query] = (result, current_time)
        print("Cached new result.")
        return result
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    """Fetch users with automatic query caching."""
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()
```

Usage Example:

```python
# First call - caches result
users = fetch_users_with_cache(query="SELECT * FROM users")
print(users)

# Second call (within 10s) - uses cache
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(users_again)

# After cache expiration - fetches fresh data
time.sleep(11)
users_expired = fetch_users_with_cache(query="SELECT * FROM users")
print(users_expired)
```

Expected Output:

```bash
(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')

First call:
Querying database and caching result.
Cached new result.
[(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]

Second call:
Returning results from cache.
[(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]

Waiting 11 seconds...
Third call (after expiration):
Cached new result.
[(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]
```

## Combined Usage

You can combine both decorators for comprehensive database function enhancement:

Basic Combination:

```python
@log_queries
@with_db_connection
def get_user_with_logging(conn, query, user_id):
    """Get user with both connection management and query logging."""
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    return cursor.fetchone()

# Usage
user = get_user_with_logging("SELECT * FROM users WHERE id = ?", user_id=1)
```

Advanced Combination:

```python
@log_queries
@with_db_connection
@cache_query
@retry_on_failure(retries=3, delay=1)
@transactional
def complex_database_operation(conn, query, params):
    """Complex operation with logging, connection, caching, retry, and transactions."""
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()

# Usage
results = complex_database_operation(
    "SELECT * FROM users WHERE active = ?", 
    (1,)
)
```

## How They Work

### Log Queries Decorator (How It Works)

1. **Decoration**: Wraps the target function
2. **Argument Extraction**: Extracts the SQL query from function arguments
3. **Logging**: Prints the query to stdout before execution
4. **Execution**: Calls the original function with all original arguments
5. **Return**: Returns the result from the original function

### Database Connection Decorator (How It Works)

1. **Setup**: Creates database connection
2. **Injection**: Passes connection as first argument to the decorated function
3. **Execution**: Calls the original function with the connection
4. **Cleanup**: Ensures connection is closed in finally block (even on errors)
5. **Return**: Returns the result from the original function

### Transaction Management Decorator (How It Works)

1. **Execution**: Calls the original function within a try-except block
2. **Success Path**: Commits the transaction if no exceptions occur
3. **Error Path**: Rolls back the transaction if any exception is raised
4. **Exception Handling**: Re-raises the original exception after rollback
5. **Return**: Returns the result from the original function

### Retry on Failure Decorator (HowIt Works)

1. **Loop**: Attempts to execute the function up to retries times
2. **Success Path**: Returns the result immediately on successful execution
3. **Error Path**: Catches exceptions and logs attempt failures
4. **Delay**: Waits for specified delay between attempts (except after last attempt)
5. **Final Failure**: Raises the last exception if all attempts fail

### Query Caching Decorator (How It Works)

1. **Cache Check**: Looks for existing cache entry when function is called
2. **Expiration Check**: Validates if cached result is still fresh (within 10 seconds)
3. **Cache Hit**: Returns cached result immediately if valid
4. **Cache Miss**: Executes query and stores result with current timestamp
5. Automatic Refresh: Expired entries trigger fresh database queries

#### Decorator Stacking Order

When using multiple decorators, they are applied bottom-up. The order matters for proper functionality:

```python
@with_db_connection # 5th: Connection management
@cache_query    # 4th: Result caching
@retry_on_failure(retries=3)    # 3rd: Error retries
@transactional  # 2nd: Transaction handling
def get_data(conn, query):  # 1st: Original function
    # Implementation
```

**Execution Order**:

1. Transaction management
2. Retry on failure
3. Query caching
4. Connection management

## Argument Handling

### Log Queries Decorator

* **Positional Arguments**: `fetch_all_users("SELECT * FROM users")`
* **Keyword Arguments**: `fetch_all_users(query="SELECT * FROM users")`
* **Fallback**: Logs `"No query provided"` if query not found

### Database Connection Decorator

* **Connection Injection**: Automatically passes `conn` as first parameter
* **Argument Forwarding**: All other arguments passed through unchanged
* **Error Safety**: Connection cleanup guaranteed via try/finally

### Transaction Management Decorator

* **Connection Required**: Must be used with `@with_db_connection` or similar
* **Automatic Commit**: Commits transaction on successful execution
* **Automatic Rollback**: Rolls back transaction on any exception
* **Exception Propagation**: Re-raises original exceptions after rollback

### Retry on Failure Decorator

* **Configurable Attempts**: Specify number of retries (default: 3)
* **Configurable Delay**: Specify delay between retries in seconds (default: 1)
* **Exception Handling**: Preserves and re-raises the last exception
* **Attempt Logging**: Logs each failed attempt with error details

### Query Caching Decorator

* **Query-Based Caching**: Uses SQL query string as cache key
* **Time-Based Expiration**: Default 10-second cache lifetime
* **Transparent Updates**: Automatically refreshes stale cache
* **Connection Handling**: Requires connection from `@with_db_connection`

## Best Practices

1. **Connection Management**: Always use the connection decorator for functions that need database access
2. **Transaction Safety**: Use transaction decorator for operations that modify data
3. **Query Logging**: Use query logging decorator during development and debugging
4. **Decorator Order**: Place @with_db_connection before @transactional
5. **Error Handling**: Both decorators handle errors gracefully
6. **Resource Cleanup**: Connections are automatically closed, preventing resource leaks
7. **Function Signatures**: Decorated functions must accept `conn` as first parameter when using `@with_db_connection`

## File Structure

```text
python-decorators/
├── 0-log_queries.py
├── 1-with_db_connection.py
├── 2-transactional.py
├── 3-retry_on_failure.py
├── 4-cache_query.py
├── users.db
└── README.md
```

## Django Integration

For Django projects, consider using Django's built-in connection management:

```python
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

def log_queries_django(func):
    """Django-compatible query logging decorator."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Executing database operation: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

def retry_on_failure_django(retries=3, delay=1):
    """Django-compatible retry decorator with proper logging."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1}/{retries} failed for {func.__name__}: {str(e)}")
                    if attempt < retries - 1:
                        time.sleep(delay)
            
            logger.error(f"All {retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator

@retry_on_failure_django(retries=3, delay=1)
@transaction.atomic
def update_user_email_django(user_id, new_email):
    """Django model operation with retry and transaction management."""
    from myapp.models import User
    user = User.objects.get(id=user_id)
    user.email = new_email
    user.save()
    return user
```

## Testing

```python
# Test setup
def setup_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT
        )
    ''')
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email) VALUES (1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')")
    conn.commit()
    conn.close()

# Run tests
if __name__ == "__main__":
    setup_database()
    
    # Test connection decorator
    user = get_user_by_id(user_id=1)
    print(f"User: {user}")
    
    # Test query logging
    users = fetch_all_users("SELECT * FROM users")
    print(f"All users: {users}")

    # Test transaction decorator
    update_user_email(user_id=1, new_email="updated@example.com")
    
    # Verify update
    updated_user = get_user_by_id(user_id=1)
    print(f"Updated user: {updated_user}")

# Test caching functionality
print("\nTesting cache:")
# First call - cache miss
users = fetch_users_with_cache(query="SELECT * FROM users")
print(f"First call: {users}")

# Second call - cache hit
users_again = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Second call: {users_again}")

# Wait for cache expiration
time.sleep(11)
# Third call - cache expired
users_expired = fetch_users_with_cache(query="SELECT * FROM users")
print(f"Third call: {users_expired}")
```

## Expected Output

```bash
Executing SQL Query: SELECT * FROM users
User: (1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')
All users: [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]

Testing cache:
Querying database and caching result.
Cached new result.
First call: [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]
Returning results from cache.
Second call: [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]
Cache expired. Querying database again.
Cached new result.
Third call: [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]
```

## License

This project is part of the ALX Backend ProDEV Software Engineering curriculum.
