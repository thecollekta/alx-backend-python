# Python Generators - Database Seeding Project

## Overview

This project implements a robust database seeding system for the ALX_prodev database using Python and MySQL. The system follows Django best practices and industry standards for database operations, error handling, and code structure.

## Features

-**Secure Database Connection**: Environment variable-based configuration
-**Robust Error Handling**: Custom exceptions and comprehensive logging
-**Data Validation**: Input validation and sanitization
-**Batch Processing**: Efficient data insertion with batch operations
-**UTF8MB4 Support**: Full Unicode character support
-**Proper Indexing**: Optimized database performance
-**Logging**: Comprehensive logging for debugging and monitoring

## Project Structure

```text
alx-backend-python/
├── seed.py           # Main seeding script
├── user_data.csv     # Sample data file
├── 0-main.py         # Test script
└── README.md
```

## Database Schema

### user_data Table

| Field | Type | Constraints |
|-------|------|-------------|
| user_id | CHAR(36) | Primary Key, UUID, Indexed |
| name | VARCHAR(255) | NOT NULL |
| email | VARCHAR(255) | NOT NULL, Indexed |
| age | DECIMAL(3,0) | NOT NULL, CHECK (0-150), Indexed |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE |

## Prerequisites

### System Requirements

- Python 3.12+
- MySQL 8.0+
- pip (Python package manager)

### Python Dependencies

```bash
pip install mysql-connector-python
```

## Environment Configuration

### Environment Variables

Create a `.env` file or set the following environment variables:

```bash

# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
```

### MySQL Setup

1. Install MySQL server
2. Create a MySQL user with appropriate privileges:

```sql
CREATE USER 'use-your-name'@'localhost' IDENTIFIED BY'secure_password';
GRANT ALL PRIVILEGES ON *.* TO 'use-your-name' @ 'localhost';
FLUSH PRIVILEGES;
```

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/alx-backend-python.git
    cd alx-backend-python/alx-backend-python
    ```

2. Install dependencies:

    ```bash
    pip install mysql-connector-python
    ```

3. Configure your environment variables

4. Ensure your CSV file is in the correct format:

```csv
name,email,age
John Doe,john@example.com,25
Jane Smith,jane@example.com,30
```

## Usage

### Command Line Usage

```bash
# Run the seeding script
python3 seed.py

# Run with the test script
python3 0-main.py
```

### Programmatic Usage

```python
import seed

# Connect to MySQL server
connection = seed.connect_db()
if connection:
    # Create database
    seed.create_database(connection)
    connection.close()

    # Connect to ALX_prodev database
    connection = seed.connect_to_prodev()
    if connection:
        # Create table and insert data
        seed.create_table(connection)
        seed.insert_data(connection, 'user_data.csv')
        connection.close()
```

## API Reference

### Functions

#### `connect_db() -> Optional[MySQLConnection]`

Establishes connection to MySQL database server.

**Returns:**

-`MySQLConnection`: Active database connection
-`None`: If connection fails

**Raises:**

-`DatabaseError`: If connection cannot be established

#### `create_database(connection: MySQLConnection) -> None`

Creates the ALX_prodev database if it doesn't exist.

**Parameters:**

-`connection`: Active MySQL connection

**Raises:**

-`DatabaseError`: If database creation fails

#### `connect_to_prodev() -> Optional[MySQLConnection]`

Connects to the ALX_prodev database specifically.

**Returns:**

-`MySQLConnection`: Active database connection

-`None`: If connection fails

#### `create_table(connection: MySQLConnection) -> None`

Creates the user_data table with proper schema and indexes.

**Parameters:**

-`connection`: Active MySQL connection to ALX_prodev database

#### `insert_data(connection: MySQLConnection, csv_file_path: str) -> None`

Inserts data from CSV file into user_data table.

**Parameters:**

-`connection`: Active MySQL connection to ALX_prodev database
-`csv_file_path`: Path to CSV file containing user data

**Raises:**

-`DatabaseError`: If data insertion fails
-`FileNotFoundError`: If CSV file doesn't exist

## Error Handling

The script implements comprehensive error handling:

-**DatabaseError**: Custom exception for database-related errors
-**Connection Errors**: Handled with retry logic and clear error messages
-**Data Validation**: Invalid data is logged and skipped
-**File Errors**: Missing files are reported with clear messages

## Security Considerations

-**Environment Variables**: Sensitive data stored in environment variables
-**SQL Injection Prevention**: Parameterized queries used throughout
-**Input Validation**: All user data is validated and sanitized
-**Connection Security**: SSL support and secure connection options

## Performance Optimizations

-**Batch Processing**: Data inserted in batches of 100 records
-**Proper Indexing**: Strategic indexes on frequently queried columns
-**Connection Pooling**: Efficient connection management
-**Memory Management**: Streaming CSV processing for large files

## Testing

Run the test script to verify functionality:

```bash
python 0-main.py
```

Expected output:

```bash
2025-07-06 17:52:17,188 - seed - INFO - Successfully connected to MySQL server
2025-07-06 17:52:17,190 - seed - INFO - Database ALX_prodev already exists
connection successful
2025-07-06 17:52:17,201 - seed - INFO - Successfully connected to ALX_prodev database
2025-07-06 17:52:17,204 - seed - INFO - Table user_data already exists
2025-07-06 17:52:17,206 - seed - INFO - Data already exists in user_data table (1000 rows)
Database ALX_prodev is present 
[('004eba9f-acba-4efa-9312-71384c0e0815', 'Cora Zieme-Schinner', 'clifford66@hotmail.com', Decimal('82'), datetime.datetime(2025, 7, 6, 17, 47, 18), datetime.datetime(2025, 7, 6, 17, 47, 18)), ('00620d85-a23e-4320-907f-25353684b5ac', 'Mr. Carlos Hyatt', 'james90@yahoo.com', Decimal('120'), datetime.datetime(2025, 7, 6, 17, 47, 18), datetime.datetime(2025, 7, 6, 17, 47, 18)), ...]
```

**Note**: The output shows the application's comprehensive logging system in action. When the database and table already exist with data, the system intelligently detects this and reports the current state rather than attempting to recreate existing resources. The sample data shown includes UUID-based user IDs, realistic names and emails, age values as Decimal types, and proper timestamp handling for created_at and updated_at fields.

## Troubleshooting

### Common Issues

1.**MySQL Connection Refused**

- Check if MySQL server is running
- Verify credentials and host configuration

2.**Permission Denied**

- Ensure MySQL user has appropriate privileges
- Check database access permissions

3.**CSV File Not Found**

- Verify file path and permissions
- Check file encoding (should be UTF-8)

4.**Data Type Errors**

- Verify CSV data format matches expected schema
- Check for invalid age values or missing fields

### Logging

The script provides comprehensive logging. Set log level for debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License

This project is part of the ALX ProDEV curriculum.
