# Python Decorators

## Overview

A collection of Python decorators for database operations, including query logging and automatic connection management. These decorators provide clean, reusable patterns for database interaction functions.

## Features

* **Automatic Query Logging**: Monitor and debug SQL queries before execution
* **Database Connection Management**: Automatic connection lifecycle handling
* **Transaction Management**: Automatic commit/rollback handling for database operations
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

```python
@log_queries
@with_db_connection
@transactional
def complex_database_operation(conn, query, user_id, new_data):
    """Complex operation with logging, connection management, and transactions."""
    cursor = conn.cursor()
    cursor.execute(query, (new_data, user_id))
    return cursor.rowcount

# Usage
rows_affected = complex_database_operation(
    "UPDATE users SET name = ? WHERE id = ?", 
    user_id=1, 
    new_data="Updated Name"
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

#### Decorator Stacking Order

When using multiple decorators, they are applied bottom-up:

```python
@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    # Function implementation
```

**Execution Order**:

1. `transactional` wraps the original function first
2. `with_db_connectio`n wraps the result of `transactional`
3. Connection is created → Transaction is managed → Function executes

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

@transaction.atomic
def update_user_email(user_id, new_email):
    user = User.objects.get(id=user_id)
    user.email = new_email
    user.save()
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
```

## Expected Output

```bash
Executing SQL Query: SELECT * FROM users
User: (1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')
All users: [(1, 'Kwame Nkrumah', 'kwame.nkrumah@ghana.com')]
```

## License

This project is part of the ALX Backend ProDEV Software Engineering curriculum.
