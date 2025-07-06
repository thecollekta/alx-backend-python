#!/usr/bin/env python3

"""
Database seeding script for ALX_prodev project.

This module provides functionality to:
- Connect to MySQL database server
- Create ALX_prodev database if it doesn't exist
- Create user_data table with proper schema
- Seed the database with CSV data
"""

import csv
import logging
import os
import sys
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

import mysql.connector
from mysql.connector import Error
from mysql.connector.connection import MySQLConnection

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database configuration - Use environment variables for production
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "19470706@BOAgye233."),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": True,
    "raise_on_warnings": True,
}

DATABASE_NAME = "ALX_prodev"


class DatabaseError(Exception):
    """Custom exception for database operations."""

    pass


def connect_db() -> Optional[MySQLConnection]:
    """
    Connect to MySQL database server.

    Returns:
        MySQLConnection: Database connection object or None if connection fails

    Raises:
        DatabaseError: If connection cannot be established
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        logger.info("Successfully connected to MySQL server")
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL server: {e}")
        raise DatabaseError(f"Failed to connect to MySQL server: {e}")


def create_database(connection: MySQLConnection) -> None:
    """
    Create the ALX_prodev database if it doesn't exist.

    Args:
        connection: Active MySQL connection

    Raises:
        DatabaseError: If database creation fails
    """
    try:
        cursor = connection.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s",
            (DATABASE_NAME,),
        )

        if cursor.fetchone():
            logger.info(f"Database {DATABASE_NAME} already exists")
        else:
            # Create database with UTF8MB4 charset for full Unicode support
            cursor.execute(
                f"CREATE DATABASE {DATABASE_NAME} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            logger.info(f"Database {DATABASE_NAME} created successfully")

        cursor.close()

    except Error as e:
        logger.error(f"Error creating database: {e}")
        raise DatabaseError(f"Failed to create database: {e}")


def connect_to_prodev() -> Optional[MySQLConnection]:
    """
    Connect to the ALX_prodev database.

    Returns:
        MySQLConnection: Database connection object or None if connection fails

    Raises:
        DatabaseError: If connection cannot be established
    """
    try:
        config = DB_CONFIG.copy()
        config["database"] = DATABASE_NAME

        connection = mysql.connector.connect(**config)
        logger.info(f"Successfully connected to {DATABASE_NAME} database")
        return connection

    except Error as e:
        logger.error(f"Error connecting to {DATABASE_NAME} database: {e}")
        raise DatabaseError(f"Failed to connect to {DATABASE_NAME} database: {e}")


def create_table(connection: MySQLConnection) -> None:
    """
    Create user_data table if it doesn't exist.

    Args:
        connection: Active MySQL connection to ALX_prodev database

    Raises:
        DatabaseError: If table creation fails
    """
    try:
        cursor = connection.cursor()

        # Check if table exists
        cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
            (DATABASE_NAME, "user_data"),
        )

        if cursor.fetchone():
            logger.info("Table user_data already exists")
        else:
            # Create table with proper constraints and indexes
            create_table_query = """
            CREATE TABLE user_data (
                user_id CHAR(36) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL,
                age DECIMAL(3,0) NOT NULL CHECK (age >= 0 AND age <= 150),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_user_id (user_id),
                INDEX idx_email (email),
                INDEX idx_age (age)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """

            cursor.execute(create_table_query)
            logger.info("Table user_data created successfully")

        cursor.close()

    except Error as e:
        logger.error(f"Error creating table: {e}")
        raise DatabaseError(f"Failed to create table: {e}")


def _validate_user_data(row: Dict[str, Any]) -> Tuple[str, str, str, Decimal]:
    """
    Validate and sanitize user data from CSV row.

    Args:
        row: Dictionary containing user data

    Returns:
        Tuple of (user_id, name, email, age)

    Raises:
        ValueError: If data validation fails
    """
    # Generate UUID for user_id
    user_id = str(uuid.uuid4())

    # Validate and sanitize name
    name = str(row.get("name", "")).strip()
    if not name or len(name) > 255:
        raise ValueError(f"Invalid name: {name}")

    # Validate and sanitize email
    email = str(row.get("email", "")).strip().lower()
    if not email or len(email) > 255 or "@" not in email:
        raise ValueError(f"Invalid email: {email}")

    # Validate and convert age
    try:
        age = Decimal(str(row.get("age", 0)))
        if age < 0 or age > 150:
            raise ValueError(f"Invalid age: {age}")
    except (TypeError, ValueError, KeyError):
        raise ValueError(f"Invalid age value: {row.get('age')}")

    return user_id, name, email, age


def insert_data(connection: MySQLConnection, csv_file_path: str) -> None:
    """
    Insert data from CSV file into user_data table.

    Args:
        connection: Active MySQL connection to ALX_prodev database
        csv_file_path: Path to CSV file containing user data

    Raises:
        DatabaseError: If data insertion fails
        FileNotFoundError: If CSV file doesn't exist
    """
    if not os.path.exists(csv_file_path):
        raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

    try:
        cursor = connection.cursor()

        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        existing_count = cursor.fetchone()[0]

        if existing_count > 0:
            logger.info(
                f"Data already exists in user_data table ({existing_count} rows)"
            )
            cursor.close()
            return

        # Prepare insert statement
        insert_query = """
        INSERT INTO user_data (user_id, name, email, age)
        VALUES (%s, %s, %s, %s)
        """

        # Read and process CSV data
        successful_inserts = 0
        failed_inserts = 0

        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            # Use DictReader for better handling of CSV headers
            reader = csv.DictReader(csvfile)

            # Strip whitespace from headers
            reader.fieldnames = [field.strip() for field in reader.fieldnames]

            batch_data = []
            batch_size = 100  # Process in batches for better performance

            for row_num, row in enumerate(reader, start=1):
                try:
                    # Validate and prepare data
                    user_id, name, email, age = _validate_user_data(row)
                    batch_data.append((user_id, name, email, age))

                    # Insert batch when batch_size is reached
                    if len(batch_data) >= batch_size:
                        cursor.executemany(insert_query, batch_data)
                        connection.commit()
                        successful_inserts += len(batch_data)
                        batch_data = []

                except ValueError as e:
                    logger.warning(f"Skipping row {row_num}: {e}")
                    failed_inserts += 1
                    continue
                except Error as e:
                    logger.error(f"Database error on row {row_num}: {e}")
                    failed_inserts += 1
                    continue

            # Insert remaining data
            if batch_data:
                cursor.executemany(insert_query, batch_data)
                connection.commit()
                successful_inserts += len(batch_data)

        cursor.close()
        logger.info(
            f"Data insertion completed: {successful_inserts} successful, "
            f"{failed_inserts} failed"
        )

    except Error as e:
        logger.error(f"Error inserting data: {e}")
        raise DatabaseError(f"Failed to insert data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during data insertion: {e}")
        raise DatabaseError(f"Unexpected error during data insertion: {e}")


def main() -> None:
    """
    Main function to demonstrate the database setup and seeding process.

    This function is for testing purposes and follows the same pattern
    as the provided 0-main.py script.
    """
    try:
        # Connect to MySQL server
        connection = connect_db()
        if connection:
            # Create database
            create_database(connection)
            connection.close()
            logger.info("Database setup completed successfully")

            # Connect to ALX_prodev database
            connection = connect_to_prodev()
            if connection:
                # Create table and insert data
                create_table(connection)
                insert_data(connection, "user_data.csv")

                # Verify setup
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA "
                    "WHERE SCHEMA_NAME = %s",
                    (DATABASE_NAME,),
                )
                result = cursor.fetchone()
                if result:
                    logger.info(f"Database {DATABASE_NAME} is present")

                # Show sample data
                cursor.execute("SELECT * FROM user_data LIMIT 5")
                rows = cursor.fetchall()
                logger.info(f"Sample data: {rows}")

                cursor.close()
                connection.close()

    except DatabaseError as e:
        logger.error(f"Database operation failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
