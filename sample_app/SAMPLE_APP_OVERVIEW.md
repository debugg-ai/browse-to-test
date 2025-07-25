# Browse-to-Test Sample App - Complete Overview

This directory contains a comprehensive sample application that demonstrates and verifies the functionality of the live `browse-to-test` library.

## 📁 Files Overview

### Core Scripts
- **`main.py`** - Comprehensive verification script with 6 test categories
- **`simple_demo.py`** - Quick minimal demo for basic functionality
- **`verify_installation.py`** - Installation and dependency verification

### Configuration & Setup  
- **`requirements.txt`** - Package dependencies for the sample app
- **`env_template.txt`** - Environment variables template
- **`run_tests.sh`** - Automated test runner script (executable)
- **`.gitignore`** - Git ignore patterns for generated files

### Documentation
- **`README.md`** - Detailed usage instructions and troubleshooting
- **`SAMPLE_APP_OVERVIEW.md`** - This overview document

## 🚀 Quick Start Guide

### 1. Install the Library
```bash
pip install browse-to-test[all]
```

### 2. Set API Key
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Run Verification
```bash
# Quick verification
python verify_installation.py

# Simple demo
python simple_demo.py

# Full comprehensive testing
python main.py

# Or use the automated runner
./run_tests.sh
```

## 🧪 Test Categories

### 1. Basic Conversion Tests (`main.py`)
Tests the core `btt.convert()` function with:
- Playwright framework conversion
- Selenium framework conversion  
- Python language output
- Assertion and error handling options

**Sample Data Used**: Simple navigation (go to URL)

### 2. ConfigBuilder Tests (`main.py`)
Tests the fluent configuration API:
- `btt.ConfigBuilder()` fluent interface
- Advanced configuration options
- Custom timeouts and debugging
- `btt.E2eTestConverter()` usage

**Sample Data Used**: Multi-step login flow

### 3. Incremental Session Tests (`main.py`)  
Tests live/streaming script generation:
- `btt.IncrementalSession()` lifecycle
- Start session, add steps, finalize
- Real-time script building
- Step validation and progress tracking

**Sample Data Used**: Shopping cart workflow

### 4. Utility Function Tests (`main.py`)
Tests library introspection:
- `btt.list_frameworks()` - Available test frameworks
- `btt.list_ai_providers()` - Available AI providers
- Plugin discovery and capability checking

### 5. Error Handling Tests (`main.py`)
Tests robust error handling:
- Invalid framework handling
- Malformed data handling  
- Empty data edge cases
- Graceful failure modes

### 6. Advanced Features Tests (`main.py`)
Tests sophisticated capabilities:
- Sensitive data masking
- Advanced configuration options
- Quality and feature validation

## 📊 Expected Outputs

### Successful Run Results
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

### Generated Files (in `output/` directory)
- `simple_playwright_python_test.py` - Basic Playwright test
- `simple_selenium_python_test.py` - Basic Selenium test  
- `config_builder_test.py` - Advanced configuration test
- `incremental_session_test.py` - Live session test
- `advanced_features_test.py` - Advanced features test
- `test_report.txt` - Comprehensive test report

## 🎯 Use Cases

### Development Verification
Use this sample app to verify that:
- The live library is correctly installed
- API keys are properly configured
- All major features work as expected
- Generated tests are properly formatted

### Integration Testing
Test the library integration with:
- Different AI providers (OpenAI, Anthropic)
- Different frameworks (Playwright, Selenium)
- Different configuration options
- Error conditions and edge cases

### Feature Demonstration
Show stakeholders:
- How easy the library is to use
- Quality of generated test scripts
- Different usage patterns and APIs
- Error handling and robustness

### Regression Testing
Catch issues when:
- Upgrading library versions
- Changing dependencies
- Modifying configurations
- Testing in new environments

## ⚙️ Advanced Usage

### Running Specific Tests
Modify `main.py` to run only certain test categories:

```python
# Run only basic conversion tests
test_results = {}
test_results["Basic Conversion"] = test_simple_conversion(args.ai_provider, args.verbose)
```

### Custom Sample Data
Add your own automation data to `load_sample_data()`:

```python
"my_custom_flow": [
    {
        "model_output": {"action": [{"your_action": {"param": "value"}}]},
        "state": {"interacted_element": [...]},
        "metadata": {"description": "Your description"}
    }
]
```

### Different AI Providers
Test with different providers:

```bash
python main.py --ai-provider openai
python main.py --ai-provider anthropic
```

### Verbose Debugging
Get detailed output for troubleshooting:

```bash
python main.py --verbose
```

## 🔧 Troubleshooting

### Common Issues

1. **Library not found**: Install with `pip install browse-to-test[all]`
2. **Missing API key**: Set `OPENAI_API_KEY` environment variable
3. **Import errors**: Check Python version >= 3.8
4. **Permission errors**: Run `chmod +x run_tests.sh`

### Debug Steps

1. Run `python verify_installation.py` first
2. Check API key with `echo $OPENAI_API_KEY`
3. Try simple demo: `python simple_demo.py`
4. Run with verbose: `python main.py --verbose`

### Getting Help

- Check the main README.md for detailed instructions
- Look at generated test reports in `output/test_report.txt`
- Examine generated test scripts for issues
- Review error messages in verbose mode

## 📈 Performance Notes

- **Simple demo**: ~30 seconds (2 API calls)
- **Full verification**: ~2-3 minutes (6+ API calls)  
- **Network dependent**: Speed varies with AI provider response times
- **Cache friendly**: Some results may be cached by the library

## 🔄 Maintenance

### Updating Sample Data
Keep automation data realistic and representative of:
- Common user workflows (login, search, purchase)
- Various element selector types (CSS, XPath, data attributes)
- Different action types (navigation, input, clicks, waits)

### Extending Tests
When adding new tests:
1. Follow existing function naming: `test_feature_name()`
2. Add to test results dictionary in `main()`
3. Update expected outputs in README.md
4. Consider both success and failure cases

### Version Compatibility
Test with different versions of:
- browse-to-test library versions
- Python versions (3.8+)
- AI provider API versions
- Testing framework versions

---

**Total Sample App Stats:**
- **8 files** providing comprehensive verification
- **6 test categories** covering all major features  
- **3 sample workflows** (navigation, login, shopping)
- **Multiple frameworks** (Playwright, Selenium)
- **2 AI providers** (OpenAI, Anthropic)
- **Comprehensive documentation** and troubleshooting guides

This sample app serves as both a verification tool and a reference implementation for using the browse-to-test library effectively. 