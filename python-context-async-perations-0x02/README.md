# Context Manager and Asynchronous Programming

## Database Context Manager

A custom class-based context manager for handling SQLite database connections with automatic resource management and query execution.

## Overview

This project implements a context manager pattern to ensure proper database connection handling, automatically opening connections when entering a `with` block and closing them when exiting, even if exceptions occur. The project includes two main implementations:

1. **DatabaseConnection** - Basic connection management
2. **ExecuteQuery** - Query execution with parameter binding

## Features

* **Automatic Resource Management** : Connections are automatically closed when exiting the context
* **Exception Safety** : Connections are properly closed even when exceptions occur
* **Simple Interface** : Clean, Pythonic API using the `with` statement
* **Parameterized Queries**: Support for safe parameter binding to prevent SQL injection
* **Query Execution**: Direct query execution with result fetching
* **Error Handling** : Robust error handling for database operations

## Project Structure

```text
python-context-async-perations-0x02/
├── 0-databaseconnection.py
├── 1-execute.py
└── README.md
```

## Usage

### Creating a Sample Database

```python
import sqlite3

# Create a sample database with users table
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Create table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert sample data
cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", 
               ("Kwame Nkrumah", "kwame.nkrumah@ghana.com", 30))
cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", 
               ("Yaa Asantewaa", "yaa.asantewaa@ghana.com", 28))
cursor.execute("INSERT INTO users (name, email, age) VALUES (?, ?, ?)", 
               ("Okomfo Anokye", "okomfo.anokye@ghana.com", 22))

conn.commit()
conn.close()
```

### Using ExecuteQuery Context Manager

```python
from 1-execute import ExecuteQuery

# Execute a parameterized query
query = "SELECT * FROM users WHERE age > ?"
age_param = (25,)

with ExecuteQuery("users.db", query, age_param) as users:
    print("Users older than 25:")
    for user in users:
        print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
```

## Implementation Details

### Context Manager Protocol

The `DatabaseConnection` class implements the context manager protocol through two special methods:

* `__enter__()`: Called when entering the `with` block, establishes database connection
* `__exit__()`: Called when exiting the `with` block, closes the connection

### Error Handling

The context manager ensures that database connections are properly closed even when exceptions occur during database operations.

```python
try:
    with ExecuteQuery("users.db", "SELECT * FROM nonexistent_table") as results:
        print(results)
except sqlite3.OperationalError as e:
    print(f"Database error: {e}")
# Connection is automatically closed even when exception occurs
```

## Testing

To test the context manager:

```python
# Test basic functionality
with DatabaseConnection("test.db") as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER, name TEXT)")
    cursor.execute("INSERT INTO test VALUES (1, 'Test')")
    cursor.execute("SELECT * FROM test")
    print(cursor.fetchall())
```

## Best Practices Demonstrated

1. **Resource Management** : Automatic cleanup of database connections
2. **Context Manager Pattern** : Proper implementation of `__enter__` and `__exit__`
3. **Exception Safety** : Guaranteed resource cleanup
4. **Clean API** : Simple, intuitive interface
5. **Parameter Binding**: Safe handling of query parameters
6. **Single Responsibility**: Each context manager has a focused purpose
7. **Error Handling**: Robust error handling for database operations

## Common Use Cases

* **Database query operations**: Executing analytical queries with parameters
* **Batch data processing**: Processing multiple queries safely
* **Database migrations**: Safe data transfer operations
* **Data analysis scripts**: Generating reports with parameterized queries
* **Testing database operations**: Testing database operations with automatic cleanup

## Troubleshooting

### Common Issues

1. **Database not found** : Ensure the database file exists or handle creation
2. **Permission errors** : Check file permissions for the database
3. **Connection not closed** : The context manager handles this automatically

### Debug Mode

For debugging, you can enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

* Connection pooling is not implemented (suitable for single-threaded operations)
* For high-concurrency applications, consider using connection pools
* Database file locking may affect performance with multiple processes

## Security Notes

* Always use parameterized queries to prevent SQL injection
* Validate input data before database operations
* Consider using environment variables for database credentials in production

## License

This project is part of the ALX ProDEV Backend Software Engineering Python curriculum.

## References

* [Python Context Managers](https://docs.python.org/3/library/contextlib.html)
* [SQLite3 Python Documentation](https://docs.python.org/3/library/sqlite3.html)
* [PEP 343 - The &#34;with&#34; Statement](https://www.python.org/dev/peps/pep-0343/)
* [SQL Injection Prevention](https://owasp.org/www-community/attacks/SQL_Injection)
