#!/usr/bin/env python3
"""
Database streaming generator for user data.

This module implements a generator function that streams rows from the user_data
table one by one, following Django best practices and industry standards.
"""

import logging
import os
from decimal import Decimal
from typing import Any, Dict, Generator, Optional

import mysql.connector
from mysql.connector import Error as MySQLError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""

    pass


def get_database_connection() -> Optional[mysql.connector.MySQLConnection]:
    """
    Establish a connection to the ALX_prodev database.

    Returns:
        MySQLConnection: Active database connection
        None: If connection fails

    Raises:
        DatabaseConnectionError: If connection cannot be established
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "19470706@BOAgye233."),
            database="ALX_prodev",
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            autocommit=False,
        )

        if connection.is_connected():
            logger.info("Successfully connected to ALX_prodev database")
            return connection

    except MySQLError as e:
        logger.error(f"Database connection failed: {e}")
        raise DatabaseConnectionError(f"Failed to connect to database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during database connection: {e}")
        raise DatabaseConnectionError(f"Unexpected connection error: {e}")

    return None


def stream_users() -> Generator[Dict[str, Any], None, None]:
    """
    Stream user rows from the user_data table one by one.

    This generator function fetches rows from the database efficiently,
    using a single connection and cursor to minimize resource usage.

    Yields:
        Dict[str, Any]: Dictionary containing user data with keys:
            - user_id: str
            - name: str
            - email: str
            - age: int

    Raises:
        DatabaseConnectionError: If database connection fails
        MySQLError: If database query fails
    """
    connection = None
    cursor = None

    try:
        # Establish database connection
        connection = get_database_connection()
        if not connection:
            raise DatabaseConnectionError("Failed to establish database connection")

        # Create cursor with server-side processing for memory efficiency
        cursor = connection.cursor(dictionary=True, buffered=False)

        # Execute query to fetch all user data
        query = """
        SELECT 
            user_id,
            name,
            email,
            age
        FROM user_data
        ORDER BY user_id
        """

        logger.info("Executing user data streaming query")
        cursor.execute(query)

        # Stream rows one by one using generator
        for row in cursor:
            # Convert Decimal age to int for consistent output format
            if isinstance(row.get("age"), Decimal):
                row["age"] = int(row["age"])

            # Validate required fields
            if not all(key in row for key in ["user_id", "name", "email", "age"]):
                logger.warning(f"Skipping incomplete row: {row}")
                continue

            yield row

    except MySQLError as e:
        logger.error(f"Database query failed: {e}")
        raise MySQLError(f"Failed to stream users: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during user streaming: {e}")
        raise
    finally:
        # Ensure proper cleanup of database resources
        if cursor:
            try:
                cursor.close()
                logger.debug("Database cursor closed")
            except Exception as e:
                logger.error(f"Error closing cursor: {e}")

        if connection and connection.is_connected():
            try:
                connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
