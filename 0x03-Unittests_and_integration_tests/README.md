# Unittests and Integration Tests

This project contains Python tasks focused on learning unit testing and integration testing concepts. The goal is to understand how to write effective tests using Python's `unittest` framework, including techniques like mocking, parametrization, and fixtures.

## Prerequisite

- Python 3.7
- `unittest` and `parameterized` libraries
- Ubuntu 18.04 LTS
- All files should end with a new line.
- The first line of all files should be `#!/usr/bin/env python3`.
- Code must use the pycodestyle style (version 2.5).
- All files must be executable.
- All modules, classes, and functions must have documentation.

## Project Structure

```bash
├── 0x03-Unittests_and_integration_tests/
│   ├── test_utils.py              # Unit tests for utils.py
│   ├── client.py                  # Client logic
│   └── README.md                  # Project documentation
```

## Task Documentation

### [0. Parameterize a unit test](./test_utils.py)

**File**: `test_utils.py`
Tests `access_nested_map` function with valid paths. Uses parameterized testing to verify:

- Accessing top-level keys
- Accessing nested dictionaries
- Accessing deeply nested values

### [1. Parameterize a unit test](./test_utils.py)

**File**: `test_utils.py`
Tests `access_nested_map` function raises `KeyError` for invalid paths. Verifies:

- `KeyError` is raised for missing keys
- Exception message matches the missing key

### [2. Mock HTTP calls](./test_utils.py)

**File**: `test_utils.py`
Tests `get_json` function without making actual HTTP calls. Uses mocking to:

- Simulate API responses
- Verify correct URL is called
- Ensure response matches expected payload

### [3. Parameterize and patch](./test_utils.py)

**File**: `test_utils.py`
Tests the memoize decorator. Verifies:

- Method results are cached
- Underlying method is called only once
- Subsequent calls return cached result

### [4. Parameterize and patch as decorators](./test_client.py)

**File**: `test_client.py`
Tests `GithubOrgClient.org` method. Uses:

- Parameterization for different organizations
- Mocking to prevent actual API calls
- Verification of correct URL formatting

### [5. Mocking a property](./test_client.py)

**File**: `test_client.py`
Tests `GithubOrgClient._public_repos_url` property. Uses:

- Context manager patching
- Mocked organization payload
- Verification of correct URL extraction

### [6. More patching](./test_client.py)

**File**: `test_client.py`
Tests `GithubOrgClient.public_repos` method. Verifies:

- Repository names are correctly extracted
- Mocked dependencies are called properly
- Both public_repos_url and get_json are used correctly

### [7. Parameterize](./test_client.py)

**File**: `test_client.py`
Tests `GithubOrgClient.has_license` method. Uses parameterized tests for:

- Repositories with matching licenses
- Repositories with different licenses
- Expected boolean results

### [8. Integration test: fixtures](./test_client.py)

**File**: `test_client.py`
Sets up integration test environment for `GithubOrgClient`. Implements:

- Class-level setup and teardown
- Mocking of requests.get with fixtures
- Parameterized test class using fixture data

### [9. Integration tests](./test_client.py)

**File**: test_client.py
Implements integration tests for public_repos method. Tests:

- Retrieval of public repositories without license filter
- Filtering of repositories by "apache-2.0" license
- Verification against expected fixture results

## How to Run Tests

```bash
# Run all tests
python -m unittest discover

# Run specific test file
python -m unittest test_utils.py
python -m unittest test_client.py
```

## Resources

- [unittest — Unit testing framework](https://docs.python.org/3/library/unittest.html)
- [unittest.mock — mock object library](https://docs.python.org/3/library/unittest.mock.html)
- [How to mock a readonly property with mock?](https://stackoverflow.com/questions/11836436/how-to-mock-a-readonly-property-with-mock)
- [parameterized](https://pypi.org/project/parameterized/)
- [Memoization](https://en.wikipedia.org/wiki/Memoization)

