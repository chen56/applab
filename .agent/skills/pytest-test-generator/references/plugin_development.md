# Pytest Plugin Development

This document provides information about developing pytest plugins to extend testing capabilities.

## Introduction to Pytest Plugins

Pytest plugins are a way to extend or modify pytest's behavior. They can:

- Add command-line options
- Define fixtures
- Implement hooks
- Add markers
- Modify test discovery
- Change reporting

## Plugin Structure

A basic pytest plugin structure:

```python
# conftest.py or in a separate plugin module
import pytest

def pytest_addoption(parser):
    """Add command-line options to pytest."""
    parser.addoption(
        "--custom-option",
        action="store_true",
        default=False,
        help="Enable custom behavior"
    )

def pytest_configure(config):
    """Configure pytest after command-line options are parsed."""
    if config.getoption("--custom-option"):
        # Configure based on option
        pass

@pytest.fixture
def custom_fixture():
    """Define a custom fixture available to all tests."""
    return "custom value"

def pytest_runtest_setup(item):
    """Called before running each test."""
    # Perform setup for individual test
    pass

def pytest_runtest_teardown(item, nextitem):
    """Called after running each test."""
    # Perform teardown for individual test
    pass
```

## Hook Functions

Pytest provides many hooks for different stages of the testing process:

```python
def pytest_configure(config):
    """Modify configuration."""
    pass

def pytest_collection_modifyitems(config, items):
    """Called after collection of test items is performed."""
    # Example: Mark all tests in a certain directory
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

def pytest_runtest_protocol(item, nextitem):
    """Implement the runtest_setup/call/teardown protocol for the given test item."""
    # Custom test execution logic
    pass

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add additional terminal summary info."""
    terminalreporter.write_sep("-", "custom summary")
    terminalreporter.write_line("Custom summary information")
```

## Creating a Simple Plugin

Here's a complete example of a simple pytest plugin:

```python
# my_plugin.py
import pytest
import time

def pytest_addoption(parser):
    parser.addoption(
        "--benchmark",
        action="store_true",
        default=False,
        help="Enable benchmarking of tests"
    )

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_protocol(item, nextitem):
    """Add timing information to tests if benchmark option is enabled."""
    if item.config.getoption("--benchmark"):
        start_time = time.time()
        # Run the normal test protocol
        outcome = yield
        duration = time.time() - start_time
        
        # Add duration as a property to the test item
        item.user_properties.append(("duration", duration))
        print(f"\n{item.name} took {duration:.2f}s")
    else:
        yield  # Just run normally

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Display benchmark summary if enabled."""
    if config.getoption("--benchmark"):
        terminalreporter.write_sep("=", "Benchmark Summary")
        # Access durations from user_properties if available
        # (Implementation depends on what you want to show)
```

To use this plugin, you can either:

1. Put it in a `conftest.py` file in your test directory
2. Install it as a package with entry points
3. Load it via command line: `pytest --pyargs my_plugin`

## Distributing Plugins

To distribute a plugin as a package, add this to your `setup.py` or `pyproject.toml`:

For `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm[toml]>=6.2"]

[project]
name = "pytest-myplugin"
version = "0.1.0"
description = "A custom pytest plugin"
dependencies = [
    "pytest>=6.0.0"
]

[project.entry-points.pytest11]
myplugin = "my_plugin"  # myplugin is the name, my_plugin is the module
```

## Built-in Hooks Reference

Commonly used pytest hooks:

- `pytest_addoption`: Add command-line options
- `pytest_configure`: Configure pytest after option parsing
- `pytest_collection_modifyitems`: Modify collected test items
- `pytest_runtest_setup`: Called before test setup
- `pytest_runtest_call`: Called to execute the test
- `pytest_runtest_teardown`: Called after test teardown
- `pytest_report_teststatus`: Customize test status reporting
- `pytest_terminal_summary`: Add to terminal summary

## Best Practices

1. **Use unique names**: Prefix your plugin's options and fixtures to avoid conflicts
2. **Document well**: Provide clear documentation for options and behavior
3. **Handle errors gracefully**: Don't crash pytest if your plugin fails
4. **Test your plugin**: Write tests for your plugin's functionality
5. **Follow conventions**: Use standard pytest patterns and naming

## Example: Custom Marker Plugin

```python
# pytest_custom_markers.py
import pytest

def pytest_addoption(parser):
    group = parser.getgroup("custom-markers")
    group.addoption(
        "--skip-custom",
        action="store_true",
        default=False,
        help="Skip tests marked with custom markers"
    )

def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-custom"):
        # Skip tests with custom markers
        skip_custom = pytest.mark.skip(reason="Skipping due to --skip-custom")
        for item in items:
            if item.get_closest_marker("custom"):
                item.add_marker(skip_custom)
```

This plugin adds a command-line option to skip tests marked with a custom marker.