# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
- **Run all tests**: `python -m pytest`
- **Run with coverage**: `python -m pytest --cov=browse_to_test --cov-report=html`
- **Run specific test file**: `python -m pytest tests/test_<component>.py`
- **Run fast tests only**: `python -m pytest -m "not slow"`
- **Run tests with verbose output**: `python -m pytest -v`

### Development Tools
- **Install in development mode**: `pip install -e .`
- **Install dev dependencies**: `pip install -r requirements-dev.txt`
- **Full package validation**: `python validate_all.py`
- **Code formatting**: `black browse_to_test/`
- **Import sorting**: `isort browse_to_test/`
- **Type checking**: `mypy browse_to_test/`
- **Linting**: `flake8 browse_to_test tests`

### Package Management
- **Build package**: `python -m build`
- **Install with all extras**: `pip install -e .[all]`
- **Run sample app tests**: `cd sample_app && bash run_tests.sh`

## Architecture Overview

Browse-to-Test is an AI-powered library that converts browser automation data into test scripts for various frameworks (Playwright, Selenium, etc.).

### Core Components

**Main API** (`browse_to_test/__init__.py`):
- `convert()` - Simple one-line conversion function
- `convert_async()` - Async version for better performance
- `ConfigBuilder` - Fluent configuration building
- `E2eTestConverter` - Main conversion class
- `IncrementalSession` - Live incremental test generation

**Core Processing** (`browse_to_test/core/`):
- `configuration/` - Config management and builder pattern
- `orchestration/` - Main conversion logic and session management
- `processing/` - Input parsing, action analysis, context collection

**AI Integration** (`browse_to_test/ai/`):
- `factory.py` - AI provider factory (OpenAI, Anthropic, etc.)
- `providers/` - Specific AI provider implementations
- `base.py` - Common AI provider interface

**Plugin System** (`browse_to_test/plugins/`):
- `registry.py` - Plugin management system
- Framework-specific plugins (Playwright, Selenium)
- Extensible architecture for new frameworks

**Output Generation** (`browse_to_test/output_langs/`):
- Multi-language support (Python, TypeScript, JavaScript)
- Template-based code generation
- Language-specific syntax and patterns

### Key Features

- **Simple API**: One-line conversion with `btt.convert(data, framework="playwright")`
- **Async Support**: Non-blocking AI calls for better performance
- **Context-Aware**: Analyzes existing tests and project structure
- **Multi-Framework**: Playwright, Selenium support with extensible plugin system
- **Multi-Language**: Python, TypeScript, JavaScript output
- **Incremental Sessions**: Live test generation as automation happens

### Configuration System

Uses a builder pattern for clean configuration:

```python
config = btt.ConfigBuilder() \
    .framework("playwright") \
    .ai_provider("openai", model="gpt-4") \
    .language("python") \
    .include_assertions(True) \
    .build()
```

### Plugin Architecture

Framework support is handled through plugins in `browse_to_test/plugins/`:
- `PlaywrightPlugin` - Generates Playwright tests
- `SeleniumPlugin` - Generates Selenium tests
- `IncrementalPlaywrightPlugin` - Live Playwright generation

## Development Guidelines

### Testing Strategy
- Unit tests for individual components (`@pytest.mark.unit`)
- Integration tests for component interactions (`@pytest.mark.integration`)
- AI tests require API keys (`@pytest.mark.ai`)
- Use fixtures from `tests/conftest.py` for test data

### Code Quality
- All code must pass `black`, `isort`, `flake8`, and `mypy`
- Minimum test coverage: 80%
- Use the pre-commit hooks defined in `.pre-commit-config.yaml`

### Environment Variables
Set these for AI provider testing:
- `OPENAI_API_KEY` - For OpenAI tests
- `ANTHROPIC_API_KEY` - For Anthropic tests

### File Structure Patterns
- Configuration classes in `core/configuration/`
- Processing logic in `core/processing/`
- AI providers in `ai/providers/`
- Framework plugins in `plugins/`
- Language templates in `output_langs/`

## Important Implementation Notes

### Async Processing
The library supports async operations for better performance with AI calls:
- Use `AsyncIncrementalSession` for live processing
- AI calls are queued and processed efficiently
- Non-blocking step addition with `wait_for_completion=False`

### Context Collection
The system can analyze existing project files to generate better tests:
- Scans for existing test patterns
- Analyzes UI components and documentation
- Uses project context for intelligent selector generation

### Backward Compatibility
The library maintains backward compatibility with deprecated functions that show warnings:
- `convert_to_test_script()` → use `convert()`
- `start_incremental_session()` → use `IncrementalSession()`

### Error Handling
- Use strict mode for better validation: `config.processing.strict_mode = True`
- Comprehensive error messages for debugging
- Graceful fallbacks when AI services are unavailable