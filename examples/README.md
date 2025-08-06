# Browse-to-Test Examples

This directory contains comprehensive examples demonstrating the browse-to-test library's capabilities. These examples have been completely redesigned to work with the latest unified API and streamlined architecture.

## Examples Overview

### 1. **basic_usage.py** - Getting Started
The simplest way to use browse-to-test. Perfect for beginners.

**Features demonstrated:**
- Simple `convert()` function usage
- Multiple frameworks (Playwright, Selenium)
- Different languages (Python, TypeScript)
- Basic configuration options
- Error handling

**Run with:**
```bash
export OPENAI_API_KEY="your-key-here"
python examples/basic_usage.py
```

### 2. **async_usage.py** - Async Operations
Advanced async patterns for better performance and scalability.

**Features demonstrated:**
- `convert_async()` for non-blocking operations
- Parallel processing of multiple conversions
- Timeout and retry mechanisms
- Performance comparison (sync vs async)
- Script quality analysis

**Run with:**
```bash
export OPENAI_API_KEY="your-key-here"
python examples/async_usage.py
```

### 3. **incremental_session.py** - Live Test Generation
Real-time test generation as browser automation happens.

**Features demonstrated:**
- `IncrementalSession` for live updates
- Adding steps one by one
- Async session management
- Live monitoring and statistics
- Error recovery and graceful degradation

**Run with:**
```bash
export OPENAI_API_KEY="your-key-here"
python examples/incremental_session.py
```

### 4. **configuration_builder.py** - Advanced Configuration
Comprehensive configuration management using the ConfigBuilder pattern.

**Features demonstrated:**
- `ConfigBuilder` fluent interface
- Configuration presets (fast, balanced, accurate, production)
- Environment-based configuration
- File-based configuration persistence
- Configuration validation and optimization

**Run with:**
```bash
export OPENAI_API_KEY="your-key-here"
python examples/configuration_builder.py
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install browse-to-test
   ```

2. **Set up API key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

3. **Run the basic example:**
   ```bash
   python examples/basic_usage.py
   ```

4. **Check the generated files:**
   ```bash
   ls examples/output/
   ```

## Generated Output

All examples create test scripts in the `examples/output/` directory:

- **Python scripts (.py)** - For Python-based test frameworks
- **TypeScript scripts (.ts)** - For TypeScript-based test frameworks  
- **Configuration files (.json)** - Saved configurations for reuse
- **Metadata files (.json)** - Session statistics and analysis

## Example Output Structure

```
examples/output/
├── simple_playwright_test.py          # Basic Playwright test
├── selenium_test.py                   # Basic Selenium test
├── async_playwright_test.py           # Async-generated test
├── parallel_playwright_python.py     # Parallel processing result
├── incremental_session_20250805.py   # Live session result
├── basic_config_test.py              # Custom config result
├── browse_to_test_config.json        # Saved configuration
└── session_metadata_20250805.json    # Session statistics
```

## Key Features Showcased

### 🚀 **Simple API**
- One-line conversions with `btt.convert()`
- Minimal configuration required
- Sensible defaults for quick start

### ⚡ **Async Support** 
- Non-blocking operations with `convert_async()`
- Parallel processing capabilities
- Better resource utilization

### 🔧 **Flexible Configuration**
- Fluent ConfigBuilder interface
- Pre-built configuration presets
- Environment-specific settings

### 📊 **Live Sessions**
- Real-time test generation
- Step-by-step script building
- Monitoring and error recovery

### 🛡️ **Production Ready**
- Comprehensive error handling
- Security-focused data masking
- Performance optimization options

## Configuration Presets

| Preset | Use Case | AI Analysis | Context Collection | Speed |
|--------|----------|-------------|-------------------|-------|
| **Fast** | CI/CD, Quick testing | Minimal | Disabled | ⚡⚡⚡ |
| **Balanced** | General development | Standard | Enabled | ⚡⚡ |
| **Accurate** | Critical tests | Comprehensive | Deep | ⚡ |
| **Production** | Live environments | Thorough | Full | ⚡ |

## Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   Error: No AI provider API key found
   ```
   **Solution:** Set `OPENAI_API_KEY` environment variable

2. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'browse_to_test'
   ```
   **Solution:** Install with `pip install browse-to-test`

3. **Empty Scripts Generated**
   ```
   Generated script is empty or minimal
   ```
   **Solution:** Check that automation data has valid action format

### Getting Help

- Check the main library documentation: `browse_to_test/__init__.py`
- Review the unified configuration system: `browse_to_test/core/config.py`
- Examine the executor implementation: `browse_to_test/core/executor.py`

## Next Steps

After running these examples:

1. **Integrate with your automation tool** - Use the IncrementalSession for live generation
2. **Customize configurations** - Create your own ConfigBuilder presets
3. **Scale with async** - Use async patterns for better performance
4. **Deploy to production** - Use production preset with security features

## API Changes

These examples use the **new unified API** introduced in v0.2.16:

### ✅ New (Current)
```python
import browse_to_test as btt

# Simple conversion
script = btt.convert(data, framework="playwright", ai_provider="openai")

# Async conversion  
script = await btt.convert_async(data, framework="playwright")

# Incremental session
session = btt.create_session(framework="playwright")
await session.start("https://example.com")
```

### ❌ Old (Deprecated)
```python
# These patterns are deprecated
script = btt.convert_to_test_script(data, framework="playwright")
session, result = btt.start_incremental_session(framework="playwright")
```

The new API is cleaner, more powerful, and follows modern Python patterns.