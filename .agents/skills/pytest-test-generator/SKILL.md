---
name: pytest-test-generator
description: Comprehensive pytest test generation with support for fixtures, parametrization, mocking, and configuration. Use when Claude needs to create high-quality pytest tests for Python code.
---

# Pytest Test Generator

## Overview

This skill provides comprehensive guidance for generating high-quality pytest tests following the latest best practices. It covers fixtures, parametrization, mocking, configuration, and test organization patterns that ensure maintainable and effective test suites.

## Test Generation Patterns

### Basic Unit Tests
For simple function/method testing, use concise tests with clear assertions:

```python
def test_addition():
    assert add(2, 3) == 5

def test_user_creation():
    user = User("john@example.com", "John Doe")
    assert user.email == "john@example.com"
    assert user.name == "John Doe"
```

### Parametrized Tests
Use `@pytest.mark.parametrize` for testing multiple inputs efficiently:

```python
@pytest.mark.parametrize("input_a,input_b,expected", [
    (2, 3, 5),
    (0, 0, 0),
    (-1, 1, 0),
    (10, -5, 5)
])
def test_addition(input_a, input_b, expected):
    assert add(input_a, input_b) == expected

# For complex data, use pytest.param with ids
@pytest.mark.parametrize("user_data,expected_error", [
    pytest.param({"email": "invalid"}, ValueError, id="invalid_email"),
    pytest.param({"email": "valid@test.com"}, None, id="valid_email"),
], indirect=["expected_error"])
def test_user_validation(user_data, expected_error):
    if expected_error:
        with pytest.raises(expected_error):
            User(**user_data)
    else:
        user = User(**user_data)
        assert user.email == user_data["email"]
```

### Fixtures for Test Setup
Use fixtures to manage test dependencies and setup/teardown:

```python
@pytest.fixture
def sample_user():
    return User(email="test@example.com", name="Test User")

@pytest.fixture
def database_connection():
    conn = create_test_db()
    yield conn
    cleanup_test_db(conn)

@pytest.fixture
def api_client():
    client = APIClient(base_url="http://testserver")
    yield client
    client.close()

def test_user_email(sample_user):
    assert sample_user.email == "test@example.com"

def test_database_operation(database_connection):
    result = database_connection.query("SELECT * FROM users")
    assert len(result) >= 0
```

### Scope-Specific Fixtures
Choose appropriate fixture scopes for efficiency:

```python
@pytest.fixture(scope="session")  # Runs once per test session
def database_schema():
    schema = create_schema()
    yield schema
    drop_schema(schema)

@pytest.fixture(scope="module")  # Runs once per module
def shared_resource():
    resource = initialize_expensive_resource()
    yield resource
    cleanup_resource(resource)

@pytest.fixture(scope="class")  # Runs once per test class
def class_fixture():
    yield setup_class_resources()

@pytest.fixture  # Default scope="function", runs for each test
def function_fixture():
    yield setup_function_resources()
```

### Complex Fixtures with Dependencies
Create fixtures that depend on other fixtures:

```python
@pytest.fixture
def user_factory():
    def _create_user(email, name="Default Name"):
        return User(email=email, name=name)
    return _create_user

@pytest.fixture
def authenticated_user(user_factory):
    user = user_factory("auth@example.com", "Authenticated User")
    user.authenticate()
    return user

def test_authenticated_features(authenticated_user):
    assert authenticated_user.is_authenticated
```

## Test Organization Best Practices

### Using conftest.py
Place shared fixtures, hooks, and configurations in `conftest.py`:

```python
# conftest.py
import pytest
from myapp.database import create_test_session, engine, Base

@pytest.fixture(scope="session")
def db_engine():
    # Create temporary database for testing
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = create_test_session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
```

### Test Class Organization
Organize related tests in classes with descriptive names:

```python
class TestUserAuthentication:
    """Test user authentication functionality"""

    def test_valid_login(self, user_factory):
        user = user_factory("active@example.com")
        user.set_password("password123")

        result = authenticate_user(user.email, "password123")
        assert result.success
        assert result.user == user

    def test_invalid_login(self, user_factory):
        user = user_factory("inactive@example.com")

        result = authenticate_user(user.email, "wrong_password")
        assert not result.success
        assert result.error_code == "INVALID_CREDENTIALS"

class TestUserPermissions:
    """Test user permission system"""

    @pytest.mark.parametrize("role,expected_permissions", [
        ("admin", ["read", "write", "delete"]),
        ("editor", ["read", "write"]),
        ("viewer", ["read"]),
    ])
    def test_role_permissions(self, role, expected_permissions):
        user = User(role=role)
        assert set(user.permissions) == set(expected_permissions)
```

## Mocking and Patching

### Using pytest-mock
Leverage `pytest-mock` for convenient mocking:

```python
def test_external_api_call(mocker):
    # Mock external API call
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": "test"}

    mocker.patch("myapp.api.requests.get", return_value=mock_response)

    result = fetch_external_data()
    assert result == {"data": "test"}

def test_file_operations(mocker):
    # Mock file operations
    mock_open = mocker.mock_open(read_data="file content")
    mocker.patch("builtins.open", mock_open)

    result = read_config_file("config.txt")
    assert result == "file content"

    mock_open.assert_called_once_with("config.txt", "r")
```

### Context Manager Mocking
Use context managers for temporary patches:

```python
def test_with_context_manager():
    with patch("myapp.module.external_func") as mock_func:
        mock_func.return_value = "mocked_result"

        result = function_using_external_func()
        assert result == "mocked_result"
        mock_func.assert_called_once()
```

## Configuration Best Practices

### pytest.ini Configuration
Use pytest configuration files for project-wide settings:

```ini
# pytest.ini
[tool:pytest]
# Add common options
addopts =
    -ra  # Show extra test summary
    --strict-markers  # Fail on unknown markers
    --strict-config  # Fail on unknown config options
    --tb=short  # Short traceback format
    --verbose  # Verbose output
    --cov=myapp  # Enable coverage for myapp package
    --cov-report=html  # Generate HTML coverage report
    --cov-report=term-missing  # Show missing lines in terminal

# Test paths to include
testpaths = tests

# Python files to treat as test modules
python_files = test_*.py *_test.py

# Python classes to treat as test classes
python_classes = Test*

# Python functions to treat as test functions
python_functions = test_*

# Custom markers with descriptions
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    smoke: marks tests as part of smoke test suite
    regression: marks tests as regression tests
```

### pyproject.toml Configuration
Alternative configuration in pyproject.toml:

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--verbose",
    "--cov=myapp",
    "--cov-report=html",
    "--cov-report=term-missing"
]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "smoke: marks tests as part of smoke test suite",
    "regression: marks tests as regression tests"
]

[tool.coverage.run]
source = ["myapp"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
```

## Advanced Testing Techniques

### Custom Markers
Use custom markers for test categorization and filtering:

```python
import pytest

@pytest.mark.slow
def test_comprehensive_integration():
    # This test takes a long time
    pass

@pytest.mark.integration
@pytest.mark.requires_network
def test_external_service():
    # Integration test requiring network access
    pass

@pytest.mark.unit
def test_calculation_logic():
    # Fast unit test
    pass

# Run with: pytest -m "not slow" to skip slow tests
# Run with: pytest -m "integration" to run only integration tests
```

### Parametrized Fixtures
Create fixtures that accept parameters:

```python
@pytest.fixture(params=[1, 2, 3])
def number_fixture(request):
    return request.param

def test_with_param_fixture(number_fixture):
    assert number_fixture > 0

# Or use indirect parametrization
@pytest.fixture
def user_with_role(request):
    role = request.param
    return User(role=role)

@pytest.mark.parametrize("user_with_role", ["admin", "user"], indirect=True)
def test_user_roles(user_with_role):
    assert user_with_role.role in ["admin", "user"]
```

### Exception Testing
Properly test for expected exceptions:

```python
def test_raises_value_error():
    with pytest.raises(ValueError, match="Invalid input"):
        process_invalid_input("bad_value")

def test_exception_attributes():
    with pytest.raises(CustomException) as exc_info:
        problematic_function()

    assert exc_info.value.error_code == "EXPECTED_CODE"
    assert "expected message" in str(exc_info.value)
```

### Working with Temporary Files
Use pytest's tmp_path fixture for temporary file operations:

```python
import json
from pathlib import Path

def test_config_file_creation(tmp_path):
    config_file = tmp_path / "config.json"
    config_data = {"setting": "value"}

    with open(config_file, 'w') as f:
        json.dump(config_data, f)

    result = load_config(config_file)
    assert result == config_data

def test_directory_structure(tmp_path):
    # Create a directory structure for testing
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    (data_dir / "file1.txt").write_text("content1")
    (data_dir / "file2.txt").write_text("content2")

    files = list(data_dir.glob("*.txt"))
    assert len(files) == 2
```

## Performance and Quality Tips

### Test Isolation
Ensure tests are isolated and don't depend on each other:

```python
# Good: Independent tests
def test_create_user():
    user = create_user("test@example.com")
    assert user.email == "test@example.com"

def test_delete_user():
    user = create_user("delete@example.com")
    delete_user(user.id)
    assert not user_exists(user.id)

# Avoid: Tests that depend on previous test state
```

### Descriptive Test Names
Use descriptive names that clearly indicate what is being tested:

```python
# Good: Clear and descriptive
def test_calculate_discount_for_regular_customer():
    # Implementation

def test_calculate_discount_for_premium_customer_with_coupon():
    # Implementation

# Avoid: Vague names
def test_discount():  # Too vague
    # Implementation
```

### Proper Assertions
Use appropriate assertion methods for better error messages:

```python
# Good: More specific assertions
def test_list_contents():
    result = get_items()
    assert result == ["item1", "item2", "item3"]
    assert len(result) == 3
    assert "item1" in result

def test_approximate_values():
    result = calculate_pi()
    assert result == pytest.approx(3.14159, abs=1e-3)

def test_dict_contains_subset():
    result = get_user_profile()
    expected = {"name": "John", "age": 30}
    assert result.items() >= expected.items()
```

## Resources

This skill provides comprehensive guidance for creating high-quality pytest tests with best practices for fixtures, parametrization, mocking, and configuration.

### references/
Contains additional reference materials for advanced pytest topics:
- `fixtures_advanced.md`: Advanced fixture techniques and patterns
- `configuration_examples.md`: More configuration examples for different project types
- `plugin_development.md`: Information about developing pytest plugins
