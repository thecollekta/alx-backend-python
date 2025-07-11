# Context Manager and Asynchronous Programming

## Database Context Manager

A custom class-based context manager for handling SQLite database connections with automatic resource management.

## Overview

This project implements a context manager pattern to ensure proper database connection handling, automatically opening connections when entering a `with` block and closing them when exiting, even if exceptions occur.

## Features

* **Automatic Resource Management** : Connections are automatically closed when exiting the context
* **Exception Safety** : Connections are properly closed even when exceptions occur
* **Simple Interface** : Clean, Pythonic API using the `with` statement
* **Error Handling** : Robust error handling for database operations

## Project Structure

```text
python-context-async-perations-0x02/
├── 0-databaseconnection.py
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Insert sample data
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Kwame Nkrumah", "kwame.nkrumah@ghana.com"))
cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Yaa Asantewaa", "yaa.asantewaa@ghana.com"))

conn.commit()
conn.close()
```

## Implementation Details

### Context Manager Protocol

The `DatabaseConnection` class implements the context manager protocol through two special methods:

* `__enter__()`: Called when entering the `with` block, establishes database connection
* `__exit__()`: Called when exiting the `with` block, closes the connection

### Error Handling

The context manager ensures that database connections are properly closed even when exceptions occur during database operations.

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

## Common Use Cases

* Database query operations
* Batch data processing
* Database migrations
* Data analysis scripts
* Testing database operations

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
