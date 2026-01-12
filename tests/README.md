# Repcal Test Suite

Comprehensive test suite for the repcal project, covering all components.

## Test Organization

```
tests/
├── test_shared.py      # Tests for repcal_shared package
├── test_web.py         # Tests for Flask web application
├── test_bot.py         # Tests for Bluesky bot
└── test_webhook.py     # Tests for Discord webhook
```

## Quick Start

### Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
./run_tests.sh
```

Or use pytest directly:

```bash
pytest
```

## Running Specific Test Suites

### Component-Specific Tests

```bash
./run_tests.sh shared      # Shared package tests
./run_tests.sh web         # Web application tests
./run_tests.sh bot         # Bluesky bot tests
./run_tests.sh webhook     # Discord webhook tests
```

### Test Categories

```bash
./run_tests.sh unit        # Unit tests only
./run_tests.sh integration # Integration tests only
./run_tests.sh fast        # Exclude slow tests
```

## Coverage Reports

Generate coverage reports:

```bash
./run_tests.sh --coverage
```

View HTML coverage report:

```bash
open htmlcov/index.html
```

## Test Structure

### test_shared.py

Tests for the `repcal_shared` package:
- **TestRepublicanDate**: RepublicanDate class functionality
- **TestOrdinalFunction**: Ordinal number formatting (1st, 2nd, 3rd, etc.)
- **TestDatabaseFunctions**: Database engine and carpe_diem function
- **TestKubernetesFunctions**: Kubernetes utility functions

### test_web.py

Tests for the Flask web application:
- **TestRoutes**: HTTP route handlers
- **TestUtilityFunctions**: Helper functions (URL validation, time checks)
- **TestLocalTimeSubmission**: Timezone handling
- **TestDateConversion**: Gregorian to Republican date conversion

### test_bot.py

Tests for the Bluesky bot:
- **TestBotImageFetching**: Remote image fetching from website
- **TestBotDatabaseIntegration**: Database usage
- **TestBotConfiguration**: Environment variables and configuration

### test_webhook.py

Tests for the Discord webhook:
- **TestGetData**: API data fetching
- **TestConstructEmbed**: Discord embed construction
- **TestUseWebhook**: Webhook message sending
- **TestWebhookConfiguration**: Configuration and environment

## Writing New Tests

### Test Naming Convention

- Test files: `test_<component>.py`
- Test classes: `Test<Feature>`
- Test functions: `test_<specific_behavior>`

### Using Markers

Mark tests with pytest markers:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_integration():
    pass

@pytest.mark.slow
def test_slow_operation():
    pass
```

Run specific markers:

```bash
pytest -m unit           # Run unit tests
pytest -m "not slow"     # Skip slow tests
```

### Mocking External Dependencies

Use `unittest.mock` or `pytest-mock`:

```python
from unittest.mock import Mock, patch

@patch('module.external_function')
def test_with_mock(mock_func):
    mock_func.return_value = 'test_value'
    # Your test code
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -r requirements-test.txt
    ./run_tests.sh --coverage
```

## Troubleshooting

### Import Errors

Ensure you're running tests from the project root:

```bash
cd /path/to/repcal
pytest
```

### Database Tests Failing

Some tests use in-memory SQLite databases. Ensure `sqlalchemy` is installed:

```bash
pip install sqlalchemy
```

### Mock Failures

If mocks aren't working, check that you're patching the correct module path:

```python
# Patch where the object is used, not where it's defined
@patch('bot.requests.get')  # Correct
# not @patch('requests.get')  # May not work
```

## Test Coverage Goals

- **Shared Package**: 90%+ coverage
- **Web Application**: 80%+ coverage (excluding templates)
- **Bot**: 70%+ coverage (excluding external API calls)
- **Webhook**: 70%+ coverage (excluding external API calls)

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Guide](https://docs.python.org/3/library/unittest.mock.html)
- [Flask Testing](https://flask.palletsprojects.com/en/latest/testing/)
