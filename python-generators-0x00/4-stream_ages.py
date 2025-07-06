#!/usr/bin/env python3
"""
Memory-efficient aggregation using generators to compute average user age.
"""

import os

import mysql.connector
from mysql.connector import Error


def get_db_connection():
    """Establish a connection to the ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", 3306),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "19470706@BOAgye233."),
            database="ALX_prodev",
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def stream_user_ages():
    """Generator that streams user ages one by one from the database."""
    connection = get_db_connection()
    if connection is None:
        return

    cursor = None
    try:
        cursor = connection.cursor(buffered=False)
        cursor.execute("SELECT age FROM user_data")

        for (age,) in cursor:
            yield age
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        connection.close()


def calculate_average_age():
    """Calculate the average age using the age streaming generator."""
    total_age = 0
    count = 0

    for age in stream_user_ages():
        total_age += age
        count += 1

    if count == 0:
        return 0.0
    return total_age / count


if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.1f}")
