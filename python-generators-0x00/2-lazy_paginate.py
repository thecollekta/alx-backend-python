#!/usr/bin/python3
"""
Lazy Loading Paginated Data Module

This module implements lazy pagination for the ALX_prodev user database.
It provides a generator function that fetches pages of user data only when needed,
implementing efficient memory usage and on-demand data loading.
"""

import logging
from typing import Any, Dict, Generator, List

import seed
from mysql.connector import Error as MySQLError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PaginationError(Exception):
    """Custom exception for pagination-related errors."""

    pass


def paginate_users(page_size: int, offset: int) -> List[Dict[str, Any]]:
    """
    Fetch a page of users from the database with the given page size and offset.

    Args:
        page_size (int): Number of users to fetch per page
        offset (int): Number of records to skip (starting point)

    Returns:
        List[Dict[str, Any]]: List of user dictionaries containing:
            - user_id: str (UUID)
            - name: str
            - email: str
            - age: Decimal
            - created_at: datetime
            - updated_at: datetime

    Raises:
        PaginationError: If database operation fails
        ValueError: If page_size is not a positive integer
    """
    if not isinstance(page_size, int) or page_size <= 0:
        raise ValueError("page_size must be a positive integer")

    if not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    connection = None
    cursor = None

    try:
        logger.debug(f"Fetching page: page_size={page_size}, offset={offset}")

        # Establish connection to ALX_prodev database
        connection = seed.connect_to_prodev()
        if not connection:
            raise PaginationError("Failed to connect to ALX_prodev database")

        # Create cursor with dictionary=True for named column access
        cursor = connection.cursor(dictionary=True)

        # Execute query with proper parameterization to prevent SQL injection
        query = "SELECT * FROM user_data LIMIT %s OFFSET %s"
        cursor.execute(query, (page_size, offset))

        # Fetch all results for this page
        rows = cursor.fetchall()

        logger.debug(f"Successfully fetched {len(rows)} users from database")
        return rows

    except MySQLError as e:
        logger.error(f"Database error during pagination: {e}")
        raise PaginationError(f"Database error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error during pagination: {e}")
        raise PaginationError(f"Unexpected error: {e}")

    finally:
        # Ensure proper cleanup of database resources
        if cursor:
            cursor.close()
            logger.debug("Database cursor closed")
        if connection and connection.is_connected():
            connection.close()
            logger.debug("Database connection closed")


def lazy_pagination(page_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Generator function that lazily loads paginated user data from the database.

    This function implements lazy loading by fetching pages of data only when needed.
    It starts with an offset of 0 and continues fetching pages until no more data
    is available, yielding each page as it's loaded.

    Args:
        page_size (int): Number of users to fetch per page

    Yields:
        List[Dict[str, Any]]: List of user dictionaries for each page containing:
            - user_id: str (UUID)
            - name: str
            - email: str
            - age: int

    Raises:
        PaginationError: If database operation fails
        ValueError: If page_size is not a positive integer

    Example:
        >>> for page in lazy_pagination(100):
        ...     for user in page:
        ...         print(user['name'])
    """
    if not isinstance(page_size, int) or page_size <= 0:
        raise ValueError("page_size must be a positive integer")

    logger.info(f"Starting lazy pagination with page_size={page_size}")

    offset = 0
    page_count = 0
    total_users = 0

    try:
        # Single loop that continues until no more data is available
        while True:
            logger.debug(f"Fetching page {page_count + 1} with offset {offset}")

            # Fetch the current page using the paginate_users function
            page_data = paginate_users(page_size, offset)

            # If no more data is available, break the loop
            if not page_data:
                logger.info(
                    f"Pagination complete. Total pages: {page_count}, Total users: {total_users}"
                )
                break

            # Update counters
            page_count += 1
            total_users += len(page_data)

            logger.debug(f"Page {page_count} loaded with {len(page_data)} users")

            # Yield the current page (lazy loading - only loads when requested)
            yield page_data

            # Update offset for next page
            offset += page_size

    except (PaginationError, ValueError) as e:
        logger.error(f"Pagination error: {e}")
        raise

    except Exception as e:
        logger.error(f"Unexpected error during lazy pagination: {e}")
        raise PaginationError(f"Unexpected error during lazy pagination: {e}")


def lazy_paginate(page_size: int) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Alias for lazy_pagination to match the required function name.

    Args:
        page_size (int): Number of users to fetch per page

    Yields:
        List[Dict[str, Any]]: List of user dictionaries for each page

    Raises:
        PaginationError: If database operation fails
        ValueError: If page_size is not a positive integer
    """
    return lazy_pagination(page_size)


# Context manager for batch pagination operations
class LazyPaginator:
    """
    Context manager for lazy pagination operations.

    Provides a clean interface for paginated data access with proper resource management.
    """

    def __init__(self, page_size: int):
        """
        Initialize the lazy paginator.

        Args:
            page_size (int): Number of users to fetch per page
        """
        self.page_size = page_size
        self.total_pages = 0
        self.total_users = 0

    def __enter__(self):
        """Enter the context manager."""
        logger.info(f"Starting lazy pagination context with page_size={self.page_size}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and log statistics."""
        if exc_type:
            logger.error(f"Lazy pagination context exited with error: {exc_val}")
        else:
            logger.info(
                f"Lazy pagination context completed. Pages: {self.total_pages}, Users: {self.total_users}"
            )
        return False

    def paginate(self) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Generate pages of user data.

        Yields:
            List[Dict[str, Any]]: List of user dictionaries for each page
        """
        for page in lazy_pagination(self.page_size):
            self.total_pages += 1
            self.total_users += len(page)
            yield page


if __name__ == "__main__":
    """
    Test the lazy pagination functionality.
    """
    try:
        print("Testing lazy pagination with page_size=10")

        # Test basic lazy pagination
        for i, page in enumerate(lazy_pagination(10)):
            print(f"\nPage {i + 1} ({len(page)} users):")
            for user in page[:2]:  # Show first 2 users per page
                print(f"  {user['name']} - {user['email']}")

            if i >= 2:  # Only show first 3 pages for testing
                break

        print("\n" + "=" * 50)

        # Test context manager
        print("Testing with context manager:")
        with LazyPaginator(5) as paginator:
            for i, page in enumerate(paginator.paginate()):
                print(f"Page {i + 1}: {len(page)} users")
                if i >= 1:  # Only show first 2 pages
                    break

    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"Error: {e}")
