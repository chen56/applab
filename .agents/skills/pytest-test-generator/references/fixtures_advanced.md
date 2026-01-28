# Advanced Pytest Fixtures

This document covers advanced fixture techniques and patterns that go beyond the basics covered in the main SKILL.md.

## Factory Fixtures

Factory fixtures return a function that can be called to create objects with different parameters:

```python
@pytest.fixture
def user_factory():
    created_users = []
    
    def _create_user(email, name="Default Name", active=True):
        user = User(email=email, name=name, active=active)
        created_users.append(user)
        return user
    
    yield _create_user
    
    # Cleanup after all tests in the scope are done
    for user in created_users:
        user.delete()

def test_multiple_users(user_factory):
    user1 = user_factory("user1@example.com", "User One")
    user2 = user_factory("user2@example.com", "User Two", active=False)
    
    assert user1.email == "user1@example.com"
    assert user2.active is False
```

## Session-Scoped Fixtures with Teardown

For expensive resources that should be created once per test session:

```python
@pytest.fixture(scope="session")
def database_container():
    """Start a database container for the entire test session."""
    import docker
    
    client = docker.from_env()
    
    # Start container
    container = client.containers.run(
        "postgres:13",
        environment={
            "POSTGRES_USER": "test",
            "POSTGRES_PASSWORD": "test",
            "POSTGRES_DB": "testdb"
        },
        ports={"5432/tcp": None},  # Random port assignment
        detach=True
    )
    
    # Wait for database to be ready
    import time
    time.sleep(5)
    
    yield container
    
    # Cleanup
    container.stop()
    container.remove()
```

## Conditional Fixtures

Sometimes you want to conditionally provide a fixture based on command-line options:

```python
def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )

@pytest.fixture
def slow_test(request):
    if request.config.getoption("--runslow"):
        yield True
    else:
        pytest.skip("need --runslow option to run")
```

## Indirect Parametrization

Using fixtures as parameters to tests:

```python
@pytest.fixture
def user_data(request):
    """Fixture that receives parameters indirectly."""
    return {
        "admin": {"role": "admin", "permissions": ["read", "write", "delete"]},
        "editor": {"role": "editor", "permissions": ["read", "write"]},
        "viewer": {"role": "viewer", "permissions": ["read"]}
    }[request.param]

@pytest.mark.parametrize("user_data", ["admin", "editor", "viewer"], indirect=True)
def test_user_permissions(user_data):
    user = User(**user_data)
    assert set(user.permissions) == set(user_data["permissions"])
```

## Dynamic Fixture Generation

Generating fixtures dynamically based on test requirements:

```python
def pytest_configure(config):
    """Dynamically register fixtures based on configuration."""
    if config.getoption("--enable-integration-tests"):
        # Register integration-specific fixtures
        pass

@pytest.fixture
def dynamic_fixture(request):
    """A fixture that adapts based on the requesting test."""
    marker = request.node.get_closest_marker("use_db")
    if marker:
        # Return database-connected fixture
        db = connect_to_test_db()
        yield db
        db.close()
    else:
        # Return mock fixture
        yield MockDB()
```

## Cross-Module Fixture Sharing

Fixtures defined in one conftest.py can be overridden in subdirectories:

```python
# tests/conftest.py (base fixture)
@pytest.fixture
def api_client():
    return APIClient(base_url="https://api.example.com")

# tests/integration/conftest.py (overridden fixture)
@pytest.fixture
def api_client():
    """Override base fixture for integration tests."""
    client = APIClient(base_url="http://localhost:8000")
    client.authenticate(test_credentials)
    yield client
    client.logout()
```

## Fixture Composition Patterns

Combining multiple fixtures to create complex test scenarios:

```python
@pytest.fixture
def base_user():
    return User(email="base@example.com", name="Base User")

@pytest.fixture
def premium_features():
    return ["feature1", "feature2", "feature3"]

@pytest.fixture
def premium_user(base_user, premium_features):
    """A complex fixture composed of other fixtures."""
    base_user.add_features(premium_features)
    base_user.upgrade_to_premium()
    return base_user

def test_premium_user_functionality(premium_user):
    assert premium_user.is_premium
    assert "feature1" in premium_user.features
```

## Exception Handling in Fixtures

Properly handling exceptions in fixtures:

```python
@pytest.fixture
def resilient_resource():
    resource = None
    try:
        resource = create_resource()
        yield resource
    except ResourceCreationError as e:
        pytest.fail(f"Failed to create resource: {e}")
    finally:
        if resource:
            cleanup_resource(resource)

@pytest.fixture
def optional_resource():
    """A fixture that handles missing resources gracefully."""
    try:
        resource = create_optional_resource()
        if resource:
            yield resource
        else:
            pytest.skip("Optional resource not available")
    except OptionalResourceError:
        pytest.skip("Optional resource unavailable")
```

## Performance Optimization

Optimizing fixture performance:

```python
@pytest.fixture(scope="session")
def expensive_computation():
    """Expensive computation cached for the entire session."""
    # This will only run once per test session
    result = perform_expensive_calculation()
    return result

@pytest.fixture
def cheap_setup(expensive_computation):
    """Lightweight setup that uses the cached computation."""
    return DerivedObject(expensive_computation)

# Cache computed values within a fixture
@pytest.fixture
def cached_data_provider():
    _cache = {}
    
    def get_data(key):
        if key not in _cache:
            _cache[key] = compute_data(key)
        return _cache[key]
    
    return get_data
```

These advanced fixture techniques allow for sophisticated test setups while maintaining clean, readable, and maintainable test code.