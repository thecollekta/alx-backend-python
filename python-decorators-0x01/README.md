# Python Decorators

## Overview

A collection of Python decorators for database operations, including query logging and automatic connection management. These decorators provide clean, reusable patterns for database interaction functions.

## Features

* **Automatic Query Logging**: Monitor and debug SQL queries before execution
* **Database Connection Management**: Automatic connection lifecycle handling
* **Flexible Argument Handling**: Supports both positional and keyword arguments
* **Function Metadata Preservation**: Uses `functools.wraps` to maintain original function properties
* **Non-intrusive**: No modification required to existing database functions
* **Resource Safety**: Proper cleanup with try/finally blocks

## Installation

No external dependencies required. Only uses Python standard library modules:

```python
import sqlite3
import functools
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

#### Implementation

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

#### Usage Example

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

## Combined Usage

You can combine both decorators for comprehensive database function enhancement:

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

## How They Work

### Log Queries Decorator

1. **Decoration**: Wraps the target function
2. **Argument Extraction**: Extracts the SQL query from function arguments
3. **Logging**: Prints the query to stdout before execution
4. **Execution**: Calls the original function with all original arguments
5. **Return**: Returns the result from the original function

### Database Connection Decorator

1. **Setup**: Creates database connection
2. **Injection**: Passes connection as first argument to the decorated function
3. **Execution**: Calls the original function with the connection
4. **Cleanup**: Ensures connection is closed in finally block (even on errors)
5. **Return**: Returns the result from the original function

## Argument Handling

### Log Queries Decorator

* **Positional Arguments**: `fetch_all_users("SELECT * FROM users")`

* **Keyword Arguments**: `fetch_all_users(query="SELECT * FROM users")`
* **Fallback**: Logs `"No query provided"` if query not found

### Database Connection Decorator

* **Connection Injection**: Automatically passes `conn` as first parameter

* **Argument Forwarding**: All other arguments passed through unchanged
* **Error Safety**: Connection cleanup guaranteed via try/finally

## Best Practices

1. **Connection Management**: Always use the connection decorator for functions that need database access
2. **Query Logging**: Use query logging decorator during development and debugging
3. **Error Handling**: Both decorators handle errors gracefully
4. **Resource Cleanup**: Connections are automatically closed, preventing resource leaks
5. **Function Signatures**: Decorated functions must accept `conn` as first parameter when using `@with_db_connection`

## File Structure

```text
python-decorators/
├── 0-log_queries.py
├── 1-with_db_connection.py
├── users.db
└── README.md
```

## Django Integration

For Django projects, consider using Django's built-in connection management:

```python
from django.db import transaction

@transaction.atomic
def get_user_by_id(user_id):
    return User.objects.get(id=user_id)
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
```

## Expected Output

```bash
Executing SQL Query: SELECT * FROM users
User: (1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')
All users: [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]
```

## License

This project is part of the ALX Backend ProDEV Software Engineering curriculum.
