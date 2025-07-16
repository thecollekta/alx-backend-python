# Unittest and Integration Tests

This project covers Python testing strategies including:

- Unit testing with `unittest`
- Parameterized testing using `parameterized`
- Mocking with `unittest.mock`

## Prerequsite

- Python 3.7
- `unittest` and `parameterized` libraries
- Ubuntu 18.04 LTS
- Pycodestyle 2.5
- SQLite3 (for integration tests)
- Git and GitHub

## Project Structure

```bash
.
├── 0x03-Unittests_and_integration_tests/
│   ├── test_utils.py              # Unit tests for utils.py
│   ├── client.py                  # Client logic
│   └── README.md                  # Project documentation
```


## Tests Implemented

1. `test_access_nested_map` -  to validate successful access of nested values in a dictionary like object using parameterized inputs.

	* Example: access_nested_map({"a": {"b": 2}}, ("a", "b"))` returns `2`.

2. `test_access_map_exception` - to validate that a `KeyError` is raised when a non-existent path is accessed.

	* Example: `access_nested_map({}, ("a",)) raises `KeyError: 'a'`.

3. `TestGetJson.test_get_json` - to ensure that `utils.get_json` performs as expected without making real HTTP calls.

	* **Test performed**:
	    - The mock is called exactly once with the correct URL: 
		* `"http://example.com"` -> `{"payload": True}`
		* `"http://holberton.io"` -> `{"payload": False}`
	    - The return value matches the mocked JSON payload.

4. `momoize` decorator - uses `unittest.mock.patch` to ensure that memoized property only triggers the the underlying method once.

5.`TestGitHubOrgClient.org` - uses the `@patch` to mock the `get_json` function to avoid real HTTP calls and verifies that `get_json` is called once with the correct URL.

6. `_public_repos_url` - uses `patch.object` with `new_callable=PropertyMock` to override the behavior of the `.org` property so that we can test method `_public_repos_url` without triggering real HTTP requests.
 
