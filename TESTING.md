# Testing Guide for Browse-to-Test

This document provides a comprehensive guide to testing the Browse-to-Test library, including how to run tests, understand test structure, and contribute to the test suite.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Configuration](#configuration)
- [Development Workflow](#development-workflow)
- [Continuous Integration](#continuous-integration)
- [Contributing Tests](#contributing-tests)
- [Troubleshooting](#troubleshooting)

## Overview

The Browse-to-Test library has a comprehensive test suite that validates all components of the system, from input parsing to test script generation. The tests are designed to:

- Ensure code quality and reliability
- Validate edge cases and error conditions
- Test integration between components
- Verify compatibility across different configurations
- Provide regression testing for bug fixes

## Test Structure

The test suite is organized into the following structure:

```
tests/
├── conftest.py                    # Shared test fixtures and configuration
├── test_ai_providers.py          # Tests for AI provider implementations
├── test_action_analyzer.py       # Tests for action analysis and optimization
├── test_config.py                # Tests for configuration management
├── test_context_collector.py     # Tests for system context collection
├── test_input_parser.py          # Tests for input parsing and validation
├── test_orchestrator.py          # Tests for main orchestrator integration
└── pytest.ini                    # Pytest configuration
```

### Test Files Description

| File | Purpose | Key Components Tested |
|------|---------|----------------------|
| `test_ai_providers.py` | AI integration | OpenAI/Anthropic providers, factory pattern |
| `test_action_analyzer.py` | Action analysis | Pattern analysis, AI-powered optimization |
| `test_config.py` | Configuration | Config validation, merging, defaults |
| `test_context_collector.py` | System context | File scanning, documentation parsing |
| `test_input_parser.py` | Input parsing | Data validation, format conversion |
| `test_orchestrator.py` | Main workflow | End-to-end integration, error handling |

## Running Tests

### Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Environment Setup**:
   ```bash
   # Optional: Set up environment variables for AI providers
   export OPENAI_API_KEY="your-key-here"
   export ANTHROPIC_API_KEY="your-key-here"
   ```

### Basic Test Execution

Run all tests:
```bash
python -m pytest
```

Run with verbose output:
```bash
python -m pytest -v
```

Run specific test file:
```bash
python -m pytest tests/test_input_parser.py
```

Run specific test class:
```bash
python -m pytest tests/test_action_analyzer.py::TestActionAnalyzer
```

Run specific test method:
```bash
python -m pytest tests/test_orchestrator.py::TestE2eScriptOrchestrator::test_generate_test_script_basic
```

### Advanced Test Options

**Run tests with coverage**:
```bash
python -m pytest --cov=browse_to_test --cov-report=html
```

**Run tests in parallel**:
```bash
python -m pytest -n auto
```

**Run only fast tests** (skip slow integration tests):
```bash
python -m pytest -m "not slow"
```

**Run only network-dependent tests**:
```bash
python -m pytest -m network
```

**Run with different verbosity levels**:
```bash
python -m pytest -v          # Verbose
python -m pytest -vv         # Very verbose
python -m pytest -q          # Quiet
python -m pytest --tb=short  # Short traceback format
```

### Test Filtering

**Run tests by keyword**:
```bash
python -m pytest -k "test_parse"              # All tests with "parse" in name
python -m pytest -k "not integration"         # Exclude integration tests
python -m pytest -k "ai and not slow"         # AI tests that aren't slow
```

**Run tests by markers**:
```bash
python -m pytest -m unit                      # Unit tests only
python -m pytest -m integration               # Integration tests only
python -m pytest -m "not network"             # Skip network tests
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```bash
# Run all unit tests
python -m pytest -m unit

# Examples of unit tests
python -m pytest tests/test_config.py::TestConfig::test_config_creation
python -m pytest tests/test_input_parser.py::TestParsedAction::test_basic_creation
```

**Characteristics**:
- Fast execution (< 1 second each)
- No external dependencies
- Focused on single functions/classes
- Use mocks for dependencies

### Integration Tests

Test component interactions:

```bash
# Run integration tests
python -m pytest -m integration

# Examples
python -m pytest tests/test_orchestrator.py::TestOrchestratorIntegration
python -m pytest tests/test_action_analyzer.py::TestActionAnalyzerIntegration
```

**Characteristics**:
- Moderate execution time (1-10 seconds)
- Test real component interactions
- May use temporary files/directories
- Validate data flow between components

### End-to-End Tests

Test complete workflows:

```bash
# Run end-to-end tests
python -m pytest tests/test_orchestrator.py::TestE2eScriptOrchestrator::test_generate_test_script_with_ai_and_context
```

**Characteristics**:
- Longer execution time (10+ seconds)
- Test full user workflows
- May require network access or external services
- Validate complete functionality

### Edge Case Tests

Test error conditions and boundary cases:

```bash
# Examples of edge case tests
python -m pytest tests/test_input_parser.py::TestInputParser::test_parse_invalid_data
python -m pytest tests/test_action_analyzer.py::TestActionAnalyzerEdgeCases
```

**Characteristics**:
- Test invalid inputs
- Verify error handling
- Check boundary conditions
- Validate graceful degradation

## Configuration

### Pytest Configuration

The test suite uses `pytest.ini` for configuration:

```ini
[tool:pytest]
minversion = 6.0
addopts = 
    -ra 
    --strict-markers 
    --strict-config
    --cov=browse_to_test
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests (> 5 seconds)
    network: Tests requiring network access
    ai: Tests involving AI providers
```

### Environment Variables

Tests can be configured via environment variables:

| Variable | Purpose | Default |
|----------|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key for provider tests | None |
| `ANTHROPIC_API_KEY` | Anthropic API key for provider tests | None |
| `PYTEST_TIMEOUT` | Test timeout in seconds | 300 |
| `PYTEST_WORKERS` | Number of parallel workers | auto |

### Test Data

Test fixtures and data are defined in `conftest.py`:

```python
# Example usage in tests
def test_example(sample_automation_data, basic_config):
    # Uses pre-defined test data from conftest.py
    parser = InputParser(basic_config)
    result = parser.parse(sample_automation_data)
    assert result.total_actions > 0
```

## Development Workflow

### Running Tests During Development

1. **Quick validation** (run relevant tests):
   ```bash
   # When working on input parser
   python -m pytest tests/test_input_parser.py -x
   
   # When working on AI integration
   python -m pytest tests/test_ai_providers.py -x
   ```

2. **Pre-commit validation**:
   ```bash
   # Run fast tests before committing
   python -m pytest -m "not slow" --maxfail=5
   ```

3. **Full validation**:
   ```bash
   # Run all tests before pushing
   python -m pytest
   ```

### Test-Driven Development (TDD)

1. **Write failing test**:
   ```python
   def test_new_feature():
       # Test for feature that doesn't exist yet
       result = new_feature(input_data)
       assert result.expected_output == "expected"
   ```

2. **Run test to see it fail**:
   ```bash
   python -m pytest tests/test_new_feature.py::test_new_feature -v
   ```

3. **Implement feature to make test pass**

4. **Refactor and ensure tests still pass**

### Adding New Tests

When adding new functionality:

1. **Create test file** (if needed):
   ```bash
   touch tests/test_new_component.py
   ```

2. **Follow naming conventions**:
   - Test files: `test_*.py`
   - Test classes: `Test*`
   - Test methods: `test_*`

3. **Use appropriate fixtures**:
   ```python
   def test_with_config(basic_config):
       # Use shared config fixture
       pass
   
   def test_with_data(sample_automation_data):
       # Use shared data fixture
       pass
   ```

4. **Add appropriate markers**:
   ```python
   @pytest.mark.unit
   def test_unit_functionality():
       pass
   
   @pytest.mark.slow
   @pytest.mark.integration
   def test_slow_integration():
       pass
   ```

### Debugging Tests

**Run with debugger**:
```bash
python -m pytest --pdb tests/test_file.py::test_method
```

**Add debug output**:
```python
def test_debug_example(capfd):
    print("Debug information")
    result = function_under_test()
    captured = capfd.readouterr()
    print(f"Captured output: {captured.out}")
```

**Use logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

def test_with_logging():
    # Logs will appear in test output with -s flag
    pass
```

Run with output capture disabled:
```bash
python -m pytest -s tests/test_file.py
```

## Continuous Integration

### GitHub Actions Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/test.yml`) that:

1. **Runs on multiple Python versions** (3.8, 3.9, 3.10, 3.11)
2. **Tests different operating systems** (Ubuntu, macOS, Windows)
3. **Installs dependencies** and sets up environment
4. **Runs full test suite** with coverage reporting
5. **Uploads coverage reports** to Codecov
6. **Runs linting and code quality checks**

### Local CI Simulation

Simulate CI environment locally:

```bash
# Install all dev dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 browse_to_test tests

# Run type checking
mypy browse_to_test

# Run tests with coverage
python -m pytest --cov=browse_to_test --cov-report=xml

# Run security checks
bandit -r browse_to_test
```

### Pre-commit Hooks

Set up pre-commit hooks to run checks automatically:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Contributing Tests

### Guidelines for Test Contributions

1. **Follow existing patterns**:
   - Use similar structure to existing tests
   - Follow naming conventions
   - Use appropriate fixtures

2. **Write clear test names**:
   ```python
   # Good
   def test_parse_automation_data_with_invalid_json_raises_error():
       pass
   
   # Bad
   def test_parse_error():
       pass
   ```

3. **Add docstrings**:
   ```python
   def test_complex_functionality():
       """Test that complex functionality works correctly with edge cases."""
       pass
   ```

4. **Use appropriate assertions**:
   ```python
   # Specific assertions
   assert result.status == "success"
   assert len(result.items) == 3
   
   # Exception testing
   with pytest.raises(ValueError, match="Invalid input"):
       function_that_should_fail()
   ```

5. **Mock external dependencies**:
   ```python
   @patch('browse_to_test.external_service')
   def test_with_external_service(mock_service):
       mock_service.return_value = "expected_response"
       # Test code here
   ```

### Test Quality Checklist

Before submitting tests, ensure:

- [ ] Tests pass consistently
- [ ] Tests are independent (can run in any order)
- [ ] External dependencies are mocked
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] Test names are descriptive
- [ ] Code is well-documented
- [ ] Appropriate markers are used

### Performance Considerations

- Keep unit tests fast (< 1 second each)
- Mark slow tests with `@pytest.mark.slow`
- Use efficient test data structures
- Avoid unnecessary file I/O in unit tests
- Mock time-consuming operations

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Ensure package is installed in development mode
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Missing Dependencies**:
```bash
# Install all test dependencies
pip install -r requirements-dev.txt

# Or install specific packages
pip install pytest pytest-cov pytest-mock
```

**Test Collection Errors**:
```bash
# Check for syntax errors
python -m py_compile tests/test_file.py

# Run with verbose collection
python -m pytest --collect-only -v
```

**Slow Test Execution**:
```bash
# Run only fast tests
python -m pytest -m "not slow"

# Use parallel execution
python -m pytest -n auto

# Profile slow tests
python -m pytest --durations=10
```

### Debugging Specific Issues

**AI Provider Tests Failing**:
- Check API keys are set correctly
- Verify network connectivity
- Use mock responses for consistent testing

**File System Tests Failing**:
- Check file permissions
- Verify temporary directory cleanup
- Use appropriate path separators for OS

**Integration Tests Flaky**:
- Add appropriate wait conditions
- Mock external dependencies
- Ensure proper test isolation

### Getting Help

1. **Check existing issues**: Look for similar problems in GitHub issues
2. **Run with verbose output**: Use `-v` and `--tb=long` for detailed information
3. **Isolate the problem**: Run specific failing tests to narrow down issues
4. **Check environment**: Verify Python version, dependencies, and environment variables

## Coverage Reports

### Generating Coverage

```bash
# Generate HTML coverage report
python -m pytest --cov=browse_to_test --cov-report=html

# View report
open htmlcov/index.html
```

### Coverage Targets

- **Minimum coverage**: 80%
- **Target coverage**: 90%+
- **Critical components**: 95%+

### Understanding Coverage

- **Line coverage**: Percentage of lines executed
- **Branch coverage**: Percentage of code branches taken
- **Function coverage**: Percentage of functions called

## Best Practices

### Test Organization

1. **Group related tests** in the same file
2. **Use descriptive class names** for test grouping
3. **Order tests logically** (simple to complex)
4. **Keep tests focused** on single functionality

### Test Data Management

1. **Use fixtures** for reusable test data
2. **Keep test data small** and focused
3. **Use factories** for generating varied test data
4. **Clean up resources** after tests

### Mocking Strategy

1. **Mock external services** and APIs
2. **Mock file system operations** when appropriate
3. **Use dependency injection** for easier testing
4. **Verify mock calls** when behavior is important

### Documentation

1. **Document complex test scenarios**
2. **Explain non-obvious assertions**
3. **Provide examples** of test usage
4. **Keep documentation up-to-date**

---

For more information about testing specific components, see the individual test files and their docstrings. If you have questions or need help with testing, please open an issue on GitHub. 