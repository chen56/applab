# Pytest Configuration Examples

This document provides additional configuration examples for different types of projects using pytest.

## Django Project Configuration

For Django projects, use this configuration in `pytest.ini` or `pyproject.toml`:

```ini
# pytest.ini for Django projects
[tool:pytest]
DJANGO_SETTINGS_MODULE = myproject.settings.test
python_files = tests.py test_*.py *_tests.py
addopts = 
    --ds=myproject.settings.test
    --reuse-db
    -ra
    --strict-markers
    --cov=myproject
    --cov-report=html
    --cov-report=term-missing
testpaths = tests
markers =
    integration: marks tests as integration tests
    slow: marks tests as slow
    serial: marks tests that must run in sequence
```

Or in `pyproject.toml`:

```toml
# pyproject.toml for Django projects
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "myproject.settings.test"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
addopts = [
    "--ds=myproject.settings.test",
    "--reuse-db",
    "-ra",
    "--strict-markers",
    "--cov=myproject",
    "--cov-report=html",
    "--cov-report=term-missing"
]
testpaths = ["tests"]
markers = [
    "integration: marks tests as integration tests",
    "slow: marks tests as slow",
    "serial: marks tests that must run in sequence"
]
```

## Flask/FastAPI Project Configuration

For web frameworks like Flask or FastAPI:

```toml
# pyproject.toml for Flask/FastAPI projects
[tool.pytest.ini_options]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80"
]
testpaths = ["tests", "integration_tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "e2e: marks tests as end-to-end tests",
    "api: marks tests as API tests",
    "ui: marks tests as UI tests",
    "slow: marks tests as slow",
    "requires_network: marks tests that require network access"
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/migrations/*",
    "*/tests/*",
    "*/venv/*",
    "*/__pycache__/*",
    "setup.py",
    "manage.py"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:"
]
```

## Data Science Project Configuration

For data science projects with pandas, numpy, etc.:

```toml
# pyproject.toml for data science projects
[tool.pytest.ini_options]
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--durations=10",  # Show 10 slowest tests
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=90"
]
testpaths = ["tests", "notebooks/tests"]
python_files = ["test_*.py", "*_test.py", "test_*.ipynb", "*_test.ipynb"]
python_classes = ["Test*", "TestData*"]
python_functions = ["test_*", "test_data_*"]
markers = [
    "unit: marks tests as unit tests",
    "integration: marks tests as integration tests",
    "slow: marks tests as slow",
    "gpu: marks tests that require GPU",
    "large_data: marks tests that use large datasets"
]

# Filter warnings common in data science
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::FutureWarning",
    "ignore:numpy.ndarray size changed:RuntimeWarning"
]

[tool.coverage.run]
source = ["src"]
omit = [
    "*/venv/*",
    "*/__pycache__/*",
    "setup.py",
    "*/notebooks/*",
    "*/experiments/*"
]