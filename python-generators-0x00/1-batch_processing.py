#!/usr/bin/env python3
"""
Batch processing module for streaming and filtering user data.

This module provides efficient batch processing capabilities for large datasets
using Python generators. It follows Django best practices and industry standards
for database operations, error handling, and resource management.
"""

import logging
import os
from typing import Any, Dict, Generator, List, Optional

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


class BatchProcessingError(Exception):
    """Custom exception for batch processing errors."""

    pass


def get_database_connection() -> Optional[mysql.connector.MySQLConnection]:
    """
    Establish a connection to the ALX_prodev database with streaming optimizations.

    Returns:
        MySQLConnection: Active database connection with buffered=False for streaming
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
            buffered=False,  # Critical for streaming large datasets
            autocommit=True,
            use_unicode=True,
        )

        if connection.is_connected():
            logger.info(
                "Successfully connected to ALX_prodev database for batch processing"
            )
            return connection

    except MySQLError as e:
        logger.error(f"Database connection failed: {e}")
        raise DatabaseConnectionError(f"Failed to connect to database: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during database connection: {e}")
        raise DatabaseConnectionError(f"Unexpected connection error: {e}")

    return None


def stream_users_in_batches(
    batch_size: int,
) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Stream user rows from the user_data table in batches.

    This generator fetches data in batches to optimize memory usage while
    processing large datasets. It implements proper resource management
    and error handling.

    Args:
        batch_size (int): Number of records to fetch per batch

    Yields:
        List[Dict[str, Any]]: List of user dictionaries containing:
            - user_id: str (UUID)
            - name: str
            - email: str
            - age: int

    Raises:
        DatabaseConnectionError: If database connection fails
        BatchProcessingError: If batch processing encounters an error
        ValueError: If batch_size is not a positive integer
    """
    # Input validation
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")

    connection = None
    cursor = None

    try:
        # Establish database connection
        connection = get_database_connection()
        if not connection:
            raise DatabaseConnectionError("Unable to establish database connection")

        # Create cursor with server-side processing
        cursor = connection.cursor(dictionary=True, buffered=False)

        # Execute query to fetch all users
        query = """
            SELECT user_id, name, email, age 
            FROM user_data 
            ORDER BY user_id
        """

        logger.info(f"Starting batch processing with batch_size={batch_size}")
        cursor.execute(query)

        batch = []
        batch_count = 0

        # Process records in batches
        for row in cursor:
            batch.append(row)

            # Yield batch when it reaches the specified size
            if len(batch) >= batch_size:
                batch_count += 1
                logger.debug(f"Yielding batch {batch_count} with {len(batch)} records")
                yield batch
                batch = []  # Reset batch for next iteration

        # Yield any remaining records in the final batch
        if batch:
            batch_count += 1
            logger.debug(
                f"Yielding final batch {batch_count} with {len(batch)} records"
            )
            yield batch

        logger.info(
            f"Batch processing completed. Total batches processed: {batch_count}"
        )

    except MySQLError as e:
        logger.error(f"Database error during batch streaming: {e}")
        raise BatchProcessingError(f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during batch streaming: {e}")
        raise BatchProcessingError(f"Unexpected error: {e}")
    finally:
        # Ensure proper cleanup of resources
        if cursor:
            cursor.close()
            logger.debug("Cursor closed successfully")
        if connection and connection.is_connected():
            connection.close()
            logger.debug("Database connection closed successfully")


def batch_processing(batch_size: int) -> None:
    """
    Process user data in batches and filter users over the age of 25.

    This function demonstrates efficient batch processing by:
    1. Streaming users in batches from the database
    2. Filtering users over age 25 within each batch
    3. Printing filtered results to stdout

    Args:
        batch_size (int): Number of records to process per batch

    Raises:
        BatchProcessingError: If batch processing encounters an error
        ValueError: If batch_size is not a positive integer
    """
    # Input validation
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")

    try:
        total_processed = 0
        total_filtered = 0

        logger.info("Starting batch processing with filter: age > 25")

        # Process users in batches (Loop 1)
        for batch in stream_users_in_batches(batch_size):
            batch_filtered_count = 0

            # Filter users over age 25 within each batch (Loop 2)
            for user in batch:
                total_processed += 1

                # Apply age filter
                if user["age"] > 25:
                    print(user)  # Output filtered user
                    batch_filtered_count += 1
                    total_filtered += 1

            logger.debug(
                f"Batch processed: {len(batch)} users, "
                f"{batch_filtered_count} filtered (age > 25)"
            )

        logger.info(
            f"Batch processing completed. "
            f"Total processed: {total_processed}, "
            f"Total filtered: {total_filtered}"
        )

    except (DatabaseConnectionError, BatchProcessingError) as e:
        logger.error(f"Batch processing failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in batch processing: {e}")
        raise BatchProcessingError(f"Unexpected error: {e}")


# Context manager for advanced usage
class BatchProcessor:
    """
    Context manager for batch processing operations.

    This class provides a context manager interface for batch processing
    with automatic resource management and error handling.
    """

    def __init__(self, batch_size: int):
        """
        Initialize the batch processor.

        Args:
            batch_size (int): Number of records to process per batch
        """
        self.batch_size = batch_size
        self.connection = None

    def __enter__(self):
        """Enter the context manager and establish connection."""
        self.connection = get_database_connection()
        if not self.connection:
            raise DatabaseConnectionError("Unable to establish database connection")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and cleanup resources."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.debug("Database connection closed via context manager")

    def process_batches(
        self, filter_func=None
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Process batches with optional filtering.

        Args:
            filter_func: Optional function to filter users

        Yields:
            List[Dict[str, Any]]: Filtered batch of users
        """
        for batch in stream_users_in_batches(self.batch_size):
            if filter_func:
                filtered_batch = [user for user in batch if filter_func(user)]
                if filtered_batch:
                    yield filtered_batch
            else:
                yield batch


def main():
    """
    Main function for testing batch processing functionality.

    This function demonstrates the usage of batch processing with
    different batch sizes and error handling.
    """
    try:
        # Test with different batch sizes
        test_batch_sizes = [10, 50, 100]

        for batch_size in test_batch_sizes:
            print(f"\n--- Testing batch processing with batch_size={batch_size} ---")

            # Count total users over 25
            total_count = 0
            for batch in stream_users_in_batches(batch_size):
                for user in batch:
                    if user["age"] > 25:
                        total_count += 1

            print(f"Total users over 25: {total_count}")

            # Break after first test to avoid too much output
            break

    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise


if __name__ == "__main__":
    main()
