#!/usr/bin/env python3
"""
Test script for memory-efficient average age calculation using generators.
"""

import importlib.util
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def import_module(module_name, file_path):
    """Dynamically import a module from a file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    """Main function to test the average age calculation."""
    try:
        # Dynamically import the stream_ages module
        stream_ages = import_module("stream_ages", "4-stream_ages.py")

        # Calculate and print the average age
        average_age = stream_ages.calculate_average_age()
        print(f"Average age of users: {average_age:.1f}")

        # Additional verification
        print("Test passed: Average age calculated successfully")
    except Exception as e:
        print(f"Test failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
