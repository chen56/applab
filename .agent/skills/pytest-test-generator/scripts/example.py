#!/usr/bin/env python3
"""
Pytest Test Generator Helper Script

This script provides utilities for generating pytest tests following best practices.
It can analyze Python code and suggest appropriate test structures.
"""

import ast
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class PytestTestGenerator:
    """
    Analyzes Python code and generates pytest test templates based on best practices.
    """

    def __init__(self):
        self.functions = []
        self.classes = []
        self.imports = []

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a Python file and extract functions, classes, and imports.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return {}

        self.functions = []
        self.classes = []
        self.imports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Skip private/internal functions
                if not node.name.startswith('_'):
                    args = [arg.arg for arg in node.args.args if arg.arg != 'self']
                    self.functions.append({
                        'name': node.name,
                        'args': args,
                        'docstring': ast.get_docstring(node),
                        'line_start': node.lineno
                    })
            elif isinstance(node, ast.AsyncFunctionDef):
                # Handle async functions
                if not node.name.startswith('_'):
                    args = [arg.arg for arg in node.args.args if arg.arg != 'self']
                    self.functions.append({
                        'name': node.name,
                        'args': args,
                        'docstring': ast.get_docstring(node),
                        'line_start': node.lineno,
                        'async': True
                    })
            elif isinstance(node, ast.ClassDef):
                # Extract public methods from class
                methods = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not item.name.startswith('_') or item.name.startswith('__'):
                            args = [arg.arg for arg in item.args.args if arg.arg != 'self']
                            methods.append({
                                'name': item.name,
                                'args': args,
                                'docstring': ast.get_docstring(item),
                                'async': isinstance(item, ast.AsyncFunctionDef)
                            })

                self.classes.append({
                    'name': node.name,
                    'methods': methods,
                    'docstring': ast.get_docstring(node)
                })
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                # Collect imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        self.imports.append(f"{module}.{alias.name}")

        return {
            'functions': self.functions,
            'classes': self.classes,
            'imports': self.imports
        }

    def generate_basic_test(self, func_name: str, args: List[str]) -> str:
        """
        Generate a basic test for a function.
        """
        params = ', '.join([f'param_{i}' for i in range(len(args))])

        test_template = f'''def test_{func_name}():
    # TODO: Implement test for {func_name}
    # Example:
    # result = {func_name}({params})
    # assert result == expected_value
    pass'''

        return test_template

    def generate_parametrized_test(self, func_name: str, args: List[str]) -> str:
        """
        Generate a parametrized test for a function.
        """
        if not args:
            return self.generate_basic_test(func_name, args)

        # Create parameter combinations
        arg_names = ', '.join(args)
        test_cases = [
            tuple([f'param_val_{i}_{j}' for j in range(len(args))])
            for i in range(3)  # Generate 3 test cases
        ]

        # Format test cases for parametrize decorator
        test_cases_str = ',\n    '.join([str(case) for case in test_cases])

        test_template = f'''@pytest.mark.parametrize("{arg_names}", [
    {test_cases_str}
])
def test_{func_name}({arg_names}):
    # TODO: Implement parametrized test for {func_name}
    # Example:
    # result = {func_name}({', '.join(args)})
    # assert result == expected_value
    pass'''

        return test_template

    def generate_test_class(self, class_name: str, methods: List[Dict]) -> str:
        """
        Generate a test class for a class with its methods.
        """
        test_methods = []

        for method in methods:
            if method['name'] != '__init__':  # Skip constructor
                args = method['args']
                params = ', '.join([f'param_{i}' for i in range(len(args))])

                if method.get('async', False):
                    test_method = f'''    async def test_{method['name']}(self):
        # TODO: Implement async test for {class_name}.{method['name']}
        # Example:
        # obj = {class_name}()
        # result = await obj.{method['name']}({params})
        # assert result == expected_value
        pass'''
                else:
                    test_method = f'''    def test_{method['name']}(self):
        # TODO: Implement test for {class_name}.{method['name']}
        # Example:
        # obj = {class_name}()
        # result = obj.{method['name']}({params})
        # assert result == expected_value
        pass'''

                test_methods.append(test_method)

        test_class = f'''class Test{class_name}:
    """Test cases for {class_name} class."""

{''.join(['\n' + method for method in test_methods])}'''

        return test_class

    def generate_conftest(self) -> str:
        """
        Generate a basic conftest.py with common fixtures.
        """
        conftest_content = '''import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        yield f
        os.unlink(f.name)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup happens automatically after test


@pytest.fixture
def sample_data():
    """Provide sample data for testing."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"}
        ],
        "config": {
            "debug": True,
            "database_url": "sqlite:///test.db"
        }
    }


@pytest.fixture(scope="session")
def database_connection():
    """Session-scoped database connection for testing."""
    # Example: Create test database
    # db = create_test_database()
    # yield db
    # cleanup_test_database(db)
    pass'''

        return conftest_content


def main():
    if len(sys.argv) < 2:
        print("Usage: python example.py <python_file_path>")
        print("Analyzes a Python file and suggests pytest test templates")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)

    generator = PytestTestGenerator()
    analysis = generator.analyze_file(file_path)

    print(f"Analysis of {file_path}:")
    print("="*50)

    if analysis['functions']:
        print("\nFunctions found:")
        for func in analysis['functions']:
            print(f"  - {func['name']}({', '.join(func['args'])})")

            # Suggest a basic test
            print(f"    Suggested test:")
            print(f"    {generator.generate_basic_test(func['name'], func['args']).replace('# TODO:', '# ').replace('pass', '...')}")
            print()

    if analysis['classes']:
        print("\nClasses found:")
        for cls in analysis['classes']:
            print(f"  - {cls['name']} with {len(cls['methods'])} methods")
            for method in cls['methods']:
                if method['name'] != '__init__':
                    print(f"    - {method['name']}({', '.join(method['args'])})")

    if analysis['imports']:
        print(f"\nImports found: {', '.join(list(set(analysis['imports']))[:10])}")  # Show first 10 unique imports


if __name__ == "__main__":
    main()
