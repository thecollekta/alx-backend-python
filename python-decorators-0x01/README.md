# Python Generators

## Log Queries Decorator

A Python decorator that logs SQL queries before execution, designed for database interaction functions.

## Overview

The `log_queries` decorator provides a simple way to monitor and debug SQL queries in your Python applications. It intercepts function calls, logs the SQL query being executed, and then proceeds with the original function execution.

## Features

* **Automatic Query Logging** : Logs SQL queries before execution
* **Flexible Argument Handling** : Supports both positional and keyword arguments
* **Function Metadata Preservation** : Uses `functools.wraps` to maintain original function properties
* **Non-intrusive** : No modification required to existing database functions

## Installation

No external dependencies required. Only uses Python standard library modules:

```python
import sqlite3
import functools
```

## Usage

### Basic Implementation

```python
import sqlite3
import functools

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
        print(f"Executing SQL Query: {query}")
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

### Example Usage

```python
# Using positional argument
users = fetch_all_users("SELECT * FROM users")

# Using keyword argument
users = fetch_all_users(query="SELECT * FROM users WHERE active = 1")

# Both will output:
# Executing SQL Query: SELECT * FROM users
# Executing SQL Query: SELECT * FROM users WHERE active = 1
```

## How It Works

1. **Decoration** : The `@log_queries` decorator wraps the target function
2. **Argument Extraction** : Extracts the SQL query from function arguments
3. **Logging** : Prints the query to stdout before execution
4. **Execution** : Calls the original function with all original arguments
5. **Return** : Returns the result from the original function

## Argument Handling

The decorator handles multiple argument patterns:

### Positional Arguments

```python
fetch_all_users("SELECT * FROM users")
# query extracted from args[0]
```

### Keyword Arguments

```python
fetch_all_users(query="SELECT * FROM users")
# query extracted from kwargs.get('query')
```

### Fallback Behavior

If no query is found in either position, logs: `"No query provided"`

## File Structure

```text
python-decorators-0x01/
├── 0-log_queries.py
└── README.md
```

## Code Example

Complete working example:

```python
import sqlite3
import functools

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Handle both positional and keyword arguments
        query = args[0] if args else kwargs.get('query', 'No query provided')
        print(f"Executing SQL Query: {query}")
        return func(*args, **kwargs)
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Usage
users = fetch_all_users(query="SELECT * FROM users")
```

## Expected Output

```bash
Executing SQL Query: SELECT * FROM users
```

## Best Practices

### Django Integration

For Django applications, consider using Django's logging system instead of `print()`:

```python
import logging

logger = logging.getLogger(__name__)

def log_queries(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        query = args[0] if args else kwargs.get('query', 'No query provided')
        logger.info(f"Executing SQL Query: {query}")
        return func(*args, **kwargs)
    return wrapper
```

### Production Considerations

* Replace `print()` with proper logging
* Add query sanitization for sensitive data
* Consider performance impact of logging
* Implement log rotation for large applications

## Limitations

* **Query Parameter Assumption** : Assumes the first parameter is always the SQL query
* **Basic Logging** : Uses simple `print()` statements
* **No Query Validation** : Doesn't validate SQL syntax
* **Single Query Support** : Designed for functions with one query parameter

## Contributing

This decorator is part of the ALX Backend Python curriculum. To contribute:

1. Fork the repository
2. Create a feature branch
3. Follow PEP 8 style guidelines
4. Add tests for new functionality
5. Submit a pull request

## Repository Information

* **GitHub repository** : `alx-backend-python`
* **Directory** : `python-decorators-0x01`
* **File** : `0-log_queries.py`

## License

This project is part of the ALX Backend ProDEV Software Engineering curriculum.

## Related Resources

* [Python Decorators Documentation](https://docs.python.org/3/glossary.html#term-decorator)
* [functools.wraps Documentation](https://docs.python.org/3/library/functools.html#functools.wraps)
* [SQLite3 Python Documentation](https://docs.python.org/3/library/sqlite3.html)
