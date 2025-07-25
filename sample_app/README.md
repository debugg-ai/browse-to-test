# Browse-to-Test Sample App

This sample application demonstrates and verifies the functionality of the live browse-to-test library. It's designed to quickly test that the remote library is working correctly with various features and use cases.

## 🎯 Purpose

This sample app serves as:
- **Verification Tool**: Quickly verify the live library installation and functionality
- **Feature Demo**: Demonstrate core features of browse-to-test
- **Integration Test**: Test different frameworks, AI providers, and configurations
- **Reference Implementation**: Show best practices for using the library

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install the live library with all features
pip install browse-to-test[all]

# Or install from requirements file
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# For OpenAI (default)
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic (optional)
export ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 3. Run the Sample App

```bash
# Basic run with OpenAI
python main.py

# With Anthropic AI provider
python main.py --ai-provider anthropic

# Verbose output for debugging
python main.py --verbose

# Full options
python main.py --ai-provider openai --verbose
```

## 📋 What Gets Tested

The sample app runs comprehensive tests covering:

### 1. Basic Conversion Tests ✅
- **Simple Playwright conversion**: Convert basic navigation to Playwright test
- **Simple Selenium conversion**: Convert basic navigation to Selenium test
- **Multiple languages**: Test Python output (with framework support for JS/TS)

### 2. ConfigBuilder Tests ✅
- **Fluent interface**: Test the ConfigBuilder fluent API
- **Advanced configuration**: Test complex configurations with multiple options
- **Custom settings**: Test timeout, debugging, and feature flags

### 3. Incremental Session Tests ✅
- **Session lifecycle**: Start, add steps, finalize workflow
- **Live updates**: Real-time script generation as steps are added
- **Step validation**: Validate each step as it's processed

### 4. Utility Function Tests ✅
- **Framework listing**: Test `list_frameworks()` function
- **AI provider listing**: Test `list_ai_providers()` function
- **Library introspection**: Verify available plugins and capabilities

### 5. Error Handling Tests ✅
- **Invalid framework**: Test graceful handling of invalid frameworks
- **Invalid data**: Test handling of malformed automation data
- **Empty data**: Test behavior with empty input data

### 6. Advanced Features Tests ✅
- **Sensitive data handling**: Test password/email masking
- **Assertion generation**: Verify test assertions are included
- **Error handling**: Verify try-catch blocks are generated

## 📁 Output Files

After running, the following files are generated in `output/`:

- `simple_playwright_python_test.py` - Basic Playwright test
- `simple_selenium_python_test.py` - Basic Selenium test
- `config_builder_test.py` - Advanced configuration test
- `incremental_session_test.py` - Incremental session test
- `advanced_features_test.py` - Advanced features test
- `test_report.txt` - Comprehensive test report

## 🔧 Sample Data Used

The app uses realistic browser automation data representing common scenarios:

### Simple Navigation
```json
{
  "model_output": {"action": [{"go_to_url": {"url": "https://example.com"}}]},
  "state": {"interacted_element": []},
  "metadata": {"description": "Navigate to example.com"}
}
```

### Login Flow
- Navigate to login page
- Enter email address
- Enter password  
- Click login button
- Wait and complete

### Shopping Cart
- Navigate to shop
- Search for product
- Click search button
- Add item to cart

## 🧪 Running Individual Tests

You can modify `main.py` to run specific test categories:

```python
# Run only basic conversion tests
test_results["Basic Conversion"] = test_simple_conversion(args.ai_provider, args.verbose)

# Run only incremental session tests  
test_results["Incremental Session"] = test_incremental_session(args.ai_provider, args.verbose)
```

## 📊 Expected Results

A successful run should show:

```
🚀 Browse-to-Test Live Library Verification
============================================================

✅ PASS Simple Playwright Python conversion
✅ PASS Simple Selenium Python conversion  
✅ PASS ConfigBuilder fluent interface
✅ PASS Incremental session start
✅ PASS Incremental steps
✅ PASS Session finalization
✅ PASS List frameworks
✅ PASS List AI providers
✅ PASS Invalid framework handling
✅ PASS Invalid data handling
✅ PASS Empty data handling
✅ PASS Advanced features

Success Rate: 100.0%
🎉 All verification tests passed!
```

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Key**
   ```
   ⚠️ Warning: OPENAI_API_KEY environment variable not set!
   ```
   **Solution**: Set the appropriate API key environment variable

2. **Library Not Found**
   ```
   ❌ Error: browse-to-test library not found!
   ```
   **Solution**: Install with `pip install browse-to-test[all]`

3. **Import Errors**
   ```
   ModuleNotFoundError: No module named 'browse_to_test'
   ```
   **Solution**: Ensure library is installed in the correct Python environment

### Debug Mode

Run with `--verbose` flag to see detailed output:

```bash
python main.py --verbose
```

This shows:
- Script previews for each generated test
- Step-by-step incremental session progress
- Detailed error messages and stack traces

## 🔧 Customization

### Adding New Test Cases

Add new sample data to `load_sample_data()`:

```python
"new_flow": [
    {
        "model_output": {"action": [{"your_action": {"param": "value"}}]},
        "state": {"interacted_element": [...]},
        "metadata": {"description": "Your test case"}
    }
]
```

### Testing Different Frameworks

Modify the frameworks list in `test_simple_conversion()`:

```python
frameworks = ["playwright", "selenium", "your-framework"]
```

### Custom Configuration

Test custom configurations in `test_config_builder()`:

```python
config = btt.ConfigBuilder() \
    .framework("playwright") \
    .your_custom_option(True) \
    .build()
```

## 📚 API Reference

The sample app demonstrates these key browse-to-test APIs:

- `btt.convert()` - Simple one-line conversion
- `btt.ConfigBuilder()` - Fluent configuration builder
- `btt.E2eTestConverter()` - Main converter class  
- `btt.IncrementalSession()` - Live session management
- `btt.list_frameworks()` - List available frameworks
- `btt.list_ai_providers()` - List available AI providers

## 🤝 Contributing

To extend this sample app:

1. Add new test functions following the pattern
2. Update the test results dictionary in `main()`
3. Add new sample data as needed
4. Update this README with new test descriptions

## 📄 License

This sample app follows the same license as the browse-to-test library. 