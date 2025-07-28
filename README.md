# Browse-to-Test

**AI-Powered Browser Automation to Test Script Converter**

Browse-to-Test is a Python library that uses AI to convert browser automation data into test scripts for various testing frameworks (Playwright, Selenium, Cypress, etc.). It provides an intelligent, configurable, and extensible way to transform recorded browser interactions into maintainable test code.

> **🆕 What's New:** Async processing support for high-performance automation, language-aware comment generation, and enhanced multi-language output with proper syntax for Python, JavaScript, TypeScript, C#, and Java. See [CHANGELOG.md](CHANGELOG.md) for details.

## 🌟 Features

- **🤖 AI-Powered Conversion**: Uses OpenAI, Anthropic, or other AI providers to intelligently convert automation data
- **🧠 Context-Aware Generation**: Leverages existing tests, documentation, and system knowledge for intelligent analysis
- **⚡ Async Support**: Non-blocking asynchronous processing for high-performance automation
- **🔌 Multi-Framework Support**: Generate tests for Playwright, Selenium, Cypress, and more
- **🗣️ Multi-Language Output**: Support for Python, JavaScript, TypeScript, C#, and Java with proper syntax
- **🏗️ Plugin Architecture**: Easily extensible with custom plugins for new frameworks/languages
- **⚙️ Highly Configurable**: Comprehensive configuration system for fine-tuning output
- **🔍 Smart Analysis**: AI-powered action analysis and optimization with system context
- **📚 System Intelligence**: Analyzes existing tests, UI components, API endpoints, and documentation
- **🎯 Pattern Recognition**: Identifies similar tests and reuses established patterns
- **🔐 Sensitive Data Handling**: Automatic detection and secure handling of sensitive information
- **💬 Language-Aware Comments**: Generates appropriate comment formats for each programming language
- **📊 Validation & Preview**: Built-in validation and preview capabilities with context insights
- **🚀 Easy to Use**: Simple API with sensible defaults and intelligent recommendations

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install browse-to-test

# With AI providers
pip install browse-to-test[openai,anthropic]

# With testing frameworks  
pip install browse-to-test[playwright,selenium]

# Full installation
pip install browse-to-test[all]
```

### Basic Usage

```python
import browse_to_test as btt

# Your browser automation data
automation_data = [
    {
        "model_output": {
            "action": [{"go_to_url": {"url": "https://example.com"}}]
        },
        "state": {"interacted_element": []}
    },
    # ... more steps
]

# Convert to Playwright test script - one line!
script = btt.convert(automation_data, framework="playwright", ai_provider="openai")
print(script)
```

### Advanced Usage with ConfigBuilder

```python
import browse_to_test as btt

# Build custom configuration with fluent interface
config = btt.ConfigBuilder() \
    .framework("playwright") \
    .ai_provider("openai", model="gpt-4") \
    .language("python") \
    .include_assertions(True) \
    .include_error_handling(True) \
    .sensitive_data_keys(["username", "password"]) \
    .enable_context_collection() \
    .thorough_mode() \
    .build()

# Create converter with custom config
converter = btt.E2eTestConverter(config)
script = converter.convert(automation_data)
```

### Incremental Live Generation

```python
import browse_to_test as btt

# Start incremental session
config = btt.ConfigBuilder().framework("playwright").build()
session = btt.IncrementalSession(config)

# Start session
result = session.start("https://example.com")

# Add steps as they happen
for step_data in automation_steps:
    result = session.add_step(step_data)
    print(f"Current script:\n{result.current_script}")

# Finalize when done
final = session.finalize()
```

### Asynchronous Processing

```python
import asyncio
import browse_to_test as btt

async def main():
    # Async conversion for better performance
    config = btt.ConfigBuilder().framework("playwright").build()
    script = await btt.convert_async(automation_data, framework="playwright", ai_provider="openai")
    
    # Async incremental session
    session = btt.AsyncIncrementalSession(config)
    result = await session.start_async("https://example.com")
    
    for step_data in automation_steps:
        # Non-blocking step addition
        result = await session.add_step_async(step_data, wait_for_completion=False)
    
    final = await session.finalize_async()

asyncio.run(main())
print(f"Complete test script:\n{final.current_script}")
```

### Context-Aware Generation

```python
import browse_to_test as btt

# Enable context-aware features
config = btt.Config(
    ai=btt.AIConfig(
        provider="openai",
        model="gpt-4",
    ),
    output=btt.OutputConfig(
        framework="playwright",
        include_assertions=True,
        include_error_handling=True,
    ),
    processing=btt.ProcessingConfig(
        # Enable intelligent analysis with system context
        analyze_actions_with_ai=True,
        collect_system_context=True,
        use_intelligent_analysis=True,
        
        # Context collection settings
        include_existing_tests=True,
        include_documentation=True,
        include_ui_components=True,
        include_api_endpoints=True,
        
        # Analysis settings
        context_analysis_depth="deep",
        max_similar_tests=5,
        context_similarity_threshold=0.3,
    ),
    project_root=".",  # Project root for context collection
    verbose=True
)

orchestrator = btt.E2eScriptOrchestrator(config)

# Generate context-aware test script
test_script = orchestrator.generate_test_script(
    automation_data=automation_data,
    target_url="https://example.com/login",
    context_hints={
        "flow_type": "authentication",
        "critical_elements": ["username", "password", "submit"]
    }
)

# Preview with context insights
preview = orchestrator.preview_conversion(
    automation_data=automation_data,
    target_url="https://example.com/login"
)

print(f"Similar tests found: {len(preview.get('similar_tests', []))}")
print(f"Context quality score: {preview.get('estimated_quality_score', 0)}")
```

## 📖 Documentation

### Core Concepts

#### 1. Input Data Format

Browse-to-Test expects browser automation data in a specific JSON format:

```json
[
  {
    "model_output": {
      "action": [
        {
          "action_type": {
            "parameter1": "value1",
            "parameter2": "value2"
          }
        }
      ]
    },
    "state": {
      "interacted_element": [
        {
          "xpath": "//button[@id='submit']",
          "css_selector": "button#submit",
          "attributes": {"id": "submit", "type": "button"}
        }
      ]
    },
    "metadata": {
      "step_start_time": 1640995200.0,
      "elapsed_time": 2.5
    }
  }
]
```

#### 2. Supported Actions

| Action Type | Description | Parameters |
|-------------|-------------|------------|
| `go_to_url` | Navigate to URL | `url` |
| `input_text` | Enter text in field | `text`, `index` |
| `click_element` | Click an element | `index` |
| `scroll_down` | Scroll page down | `amount` (optional) |
| `scroll_up` | Scroll page up | `amount` (optional) |
| `wait` | Wait for time | `seconds` |
| `done` | Mark completion | `text`, `success` |

#### 3. Configuration System

The library uses a hierarchical configuration system:

```python
config = btt.Config(
    # AI Provider Settings
    ai=btt.AIConfig(
        provider="openai",          # openai, anthropic, azure, local
        model="gpt-4",              # Provider-specific model
        temperature=0.1,            # Generation randomness (0-2)
        max_tokens=4000,            # Maximum response tokens
        api_key="your-key",         # API key (or use env vars)
    ),
    
    # Output Settings
    output=btt.OutputConfig(
        framework="playwright",     # Target framework
        language="python",          # Target language
        test_type="script",         # script, test, spec
        include_assertions=True,    # Add test assertions
        include_waits=True,         # Add explicit waits
        include_error_handling=True,# Add try-catch blocks
        include_logging=True,       # Add logging statements
        sensitive_data_keys=["username", "password"],
        mask_sensitive_data=True,   # Mask sensitive data
    ),
    
    # Processing Settings  
    processing=btt.ProcessingConfig(
        analyze_actions_with_ai=True,  # Use AI for analysis
        optimize_selectors=True,       # Optimize CSS/XPath selectors
        validate_actions=True,         # Validate action feasibility
        strict_mode=False,             # Fail on any errors
        
        # Context Collection Settings
        collect_system_context=True,   # Enable context collection
        use_intelligent_analysis=True, # Use AI with system context
        include_existing_tests=True,   # Analyze existing test files
        include_documentation=True,    # Include project documentation
        include_ui_components=True,    # Analyze UI component files
        include_api_endpoints=True,    # Include API endpoint info
        include_recent_changes=True,   # Consider recent git changes
        
        # Context Analysis Settings
        context_analysis_depth="deep", # shallow, medium, deep
        max_similar_tests=5,           # Max similar tests to consider
        context_similarity_threshold=0.3, # Similarity threshold (0-1)
        max_context_files=100,         # Limit files for performance
    ),
    
    # Global Settings
    debug=False,
    verbose=False,
    log_level="INFO",
)
```

### Environment Variables

Set these environment variables for AI providers:

```bash
# OpenAI
export OPENAI_API_KEY="your-openai-key"

# Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# Azure OpenAI
export AZURE_OPENAI_API_KEY="your-azure-key"
export AZURE_OPENAI_ENDPOINT="your-azure-endpoint"

# Browse-to-Test specific
export BROWSE_TO_TEST_AI_PROVIDER="openai"
export BROWSE_TO_TEST_OUTPUT_FRAMEWORK="playwright"
export BROWSE_TO_TEST_DEBUG="true"

# Context-aware features
export BROWSE_TO_TEST_PROCESSING_COLLECT_CONTEXT="true"
export BROWSE_TO_TEST_PROCESSING_USE_INTELLIGENT_ANALYSIS="true"
export BROWSE_TO_TEST_PROCESSING_CONTEXT_ANALYSIS_DEPTH="deep"
```

## 🔌 Plugin System

Browse-to-Test uses a plugin architecture to support different frameworks and languages.

### Available Plugins

| Plugin | Frameworks | Languages | Status |
|--------|------------|-----------|--------|
| Playwright | `playwright` | `python` | ✅ Stable |
| Selenium | `selenium`, `webdriver` | `python` | ✅ Stable |
| Cypress | `cypress` | `javascript`, `typescript` | 🚧 Community |

### Creating Custom Plugins

```python
from browse_to_test.plugins.base import OutputPlugin, GeneratedTestScript

class MyCustomPlugin(OutputPlugin):
    @property
    def plugin_name(self) -> str:
        return "my-framework"
    
    @property  
    def supported_frameworks(self) -> List[str]:
        return ["my-framework"]
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python", "javascript"]
    
    def generate_test_script(self, parsed_data, analysis_results=None):
        # Your custom generation logic here
        script_content = self._generate_custom_script(parsed_data)
        
        return GeneratedTestScript(
            content=script_content,
            language=self.config.language,
            framework=self.config.framework,
        )

# Register your plugin
registry = btt.PluginRegistry()
registry.register_plugin("my-framework", MyCustomPlugin)
```

## 🛠️ API Reference

### Main Functions

#### `convert_to_test_script(automation_data, output_framework, ai_provider, config=None)`

Convert automation data to test script (convenience function).

**Parameters:**
- `automation_data`: List of automation steps or path to JSON file
- `output_framework`: Target framework ("playwright", "selenium", etc.)
- `ai_provider`: AI provider ("openai", "anthropic", etc.)
- `config`: Optional configuration dictionary

**Returns:** Generated test script as string

#### `list_available_plugins()`

List all available output framework plugins.

**Returns:** List of plugin names

#### `list_available_ai_providers()`

List all available AI providers.

**Returns:** List of provider names

### Core Classes

#### `E2eScriptOrchestrator(config)`

Main orchestrator class that coordinates the conversion process.

**Methods:**
- `generate_test_script(automation_data, custom_config=None)`: Generate test script
- `generate_with_multiple_frameworks(automation_data, frameworks)`: Generate for multiple frameworks
- `validate_configuration()`: Validate current configuration
- `preview_conversion(automation_data, max_actions=5)`: Preview conversion

#### `Config`, `AIConfig`, `OutputConfig`, `ProcessingConfig`

Configuration classes for different aspects of the library.

#### `PluginRegistry`

Registry for managing output plugins.

**Methods:**
- `register_plugin(name, plugin_class)`: Register a new plugin
- `create_plugin(config)`: Create plugin instance
- `list_available_plugins()`: List available plugins

## 📊 Examples

### Generate Multiple Frameworks

```python
orchestrator = btt.E2eScriptOrchestrator(config)
scripts = orchestrator.generate_with_multiple_frameworks(
    automation_data, 
    ["playwright", "selenium"]
)

for framework, script in scripts.items():
    with open(f"test_{framework}.py", "w") as f:
        f.write(script)
```

### Load from File

```python
# Save automation data to file
with open("automation_data.json", "w") as f:
    json.dump(automation_data, f)

# Load and convert from file
script = btt.convert_to_test_script(
    automation_data="automation_data.json",
    output_framework="playwright"
)
```

### Custom Configuration

```python
config = {
    "ai": {"provider": "anthropic", "model": "claude-3-sonnet"},
    "output": {"include_screenshots": True, "add_comments": True},
    "processing": {"analyze_actions_with_ai": False}
}

script = btt.convert_to_test_script(
    automation_data=data,
    output_framework="selenium", 
    config=config
)
```

### Preview Before Generation

```python
orchestrator = btt.E2eScriptOrchestrator(config)
preview = orchestrator.preview_conversion(automation_data)

print(f"Total steps: {preview['total_steps']}")
print(f"Total actions: {preview['total_actions']}")
print(f"Action types: {preview['action_types']}")
print(f"Validation issues: {preview['validation_issues']}")
print(f"Similar tests: {len(preview.get('similar_tests', []))}")
print(f"Quality score: {preview.get('estimated_quality_score', 0)}")
```

## ⚡ Async Processing

Browse-to-Test supports asynchronous processing to handle performance bottlenecks with AI calls and enable concurrent operations.

### Key Benefits

- **🚀 Non-blocking AI calls**: Process multiple automation steps concurrently
- **📊 Better performance**: Up to 5x faster for large automation datasets
- **🎛️ Queue management**: Intelligent queuing and throttling of AI requests
- **⏱️ Timeout handling**: Configurable timeouts with graceful error handling
- **🔄 Background processing**: Add steps without waiting for completion

### Quick Start

```python
import asyncio
import browse_to_test as btt

async def convert_multiple_datasets():
    tasks = [
        btt.convert_async(dataset1, framework="playwright", ai_provider="openai"),
        btt.convert_async(dataset2, framework="selenium", ai_provider="anthropic"),
    ]
    scripts = await asyncio.gather(*tasks)
    return scripts

# Run async code
scripts = asyncio.run(convert_multiple_datasets())
```

For detailed async documentation, see [ASYNC_README.md](ASYNC_README.md).

## 🗣️ Multi-Language Support

Generate test scripts in multiple programming languages with proper syntax and language-specific features:

| Language | Comment Style | Documentation | Framework Support |
|----------|---------------|---------------|-------------------|
| **Python** | `# comment` | `"""docstrings"""` | Playwright, Selenium |
| **JavaScript** | `// comment` | `/** JSDoc */` | Playwright |
| **TypeScript** | `// comment` | `/** TSDoc */` | Playwright |
| **C#** | `// comment` | `/// XML docs` | Planned |
| **Java** | `// comment` | `/** Javadoc */` | Planned |

### Language-Specific Output

```python
# Python example with proper syntax
config = btt.ConfigBuilder().language("python").framework("playwright").build()
script = btt.convert(automation_data, config=config)

# JavaScript example with proper syntax  
config = btt.ConfigBuilder().language("javascript").framework("playwright").build()
script = btt.convert(automation_data, config=config)
```

## 🧠 Context-Aware Features

Browse-to-Test includes powerful context-aware capabilities that analyze your existing codebase to generate more intelligent and consistent test scripts.

### How It Works

1. **Context Collection**: Scans your project for existing tests, documentation, UI components, and API endpoints
2. **Pattern Analysis**: Uses AI to understand your project's testing conventions and patterns
3. **Intelligent Generation**: Leverages this context to generate tests that align with your existing codebase
4. **Similarity Detection**: Identifies similar existing tests to avoid duplication and ensure consistency

### What Gets Analyzed

| Component | Description | Benefits |
|-----------|-------------|----------|
| **Existing Tests** | Playwright, Selenium, Cypress test files | Consistent selector patterns, test structure |
| **Documentation** | README, API docs, contributing guides | Project-specific terminology and conventions |
| **UI Components** | React, Vue, Angular component files | Component props, data attributes, CSS classes |
| **API Endpoints** | Route definitions, OpenAPI specs | Endpoint patterns, authentication flows |
| **Recent Changes** | Git history and recent commits | Awareness of recent code changes |

### Context-Aware Benefits

✨ **Consistency**: Generated tests follow your project's established patterns and conventions

🎯 **Intelligence**: AI understands your specific domain, components, and testing strategies  

🔍 **Similarity Detection**: Avoids duplicating existing test coverage

⚡ **Optimized Selectors**: Uses selectors that match your project's preferred patterns (data-testid, CSS classes, etc.)

🛡️ **Smart Defaults**: Automatically configures sensitive data handling and test setup based on existing tests

📊 **Quality Insights**: Provides quality scores and recommendations based on project analysis

### Configuration Options

```python
processing=btt.ProcessingConfig(
    # Enable context features
    collect_system_context=True,
    use_intelligent_analysis=True,
    
    # Control what gets analyzed
    include_existing_tests=True,
    include_documentation=True,
    include_ui_components=True,
    include_api_endpoints=True,
    include_database_schema=False,  # More expensive
    include_recent_changes=True,
    
    # Fine-tune analysis
    context_analysis_depth="deep",  # shallow, medium, deep
    max_similar_tests=5,
    context_similarity_threshold=0.3,
    max_context_files=100,
    
    # Performance settings
    context_cache_ttl=3600,  # Cache for 1 hour
    max_context_prompt_size=8000,
)
```

### Performance Optimization

For faster generation, use speed-optimized settings:

```python
config = btt.Config()
config.optimize_for_speed()  # Disables heavy context analysis

# Or manually configure
config.processing.collect_system_context = False
config.processing.context_analysis_depth = "shallow"
config.processing.max_context_files = 20
```

For maximum accuracy, use accuracy-optimized settings:

```python
config = btt.Config()
config.optimize_for_accuracy()  # Enables deep context analysis

# Or manually configure  
config.processing.context_analysis_depth = "deep"
config.processing.max_context_files = 200
config.ai.max_tokens = 8000
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/browse-to-test.git
cd browse-to-test

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e .[dev,all]

# Run tests
pytest

# Format code
black browse_to_test/
isort browse_to_test/

# Type checking
mypy browse_to_test/
```

### Creating a Plugin

1. Create a new plugin class inheriting from `OutputPlugin`
2. Implement required methods (`plugin_name`, `supported_frameworks`, etc.)
3. Add tests for your plugin
4. Submit a pull request

### Reporting Issues

Please use the [GitHub issue tracker](https://github.com/yourusername/browse-to-test/issues) to report bugs or request features.

## 📚 Documentation

- **[ASYNC_README.md](ASYNC_README.md)**: Comprehensive async processing guide
- **[INCREMENTAL_README.md](INCREMENTAL_README.md)**: Incremental session documentation  
- **[COMMENT_SYSTEM_UPGRADE.md](COMMENT_SYSTEM_UPGRADE.md)**: Language-specific comment system details
- **[CHANGELOG.md](CHANGELOG.md)**: Recent changes and version history

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI and Anthropic for providing powerful AI APIs
- Playwright and Selenium teams for excellent testing frameworks
- The open-source community for inspiration and contributions

## 📞 Support

- **Documentation**: [browse-to-test.readthedocs.io](https://browse-to-test.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/browse-to-test/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/browse-to-test/discussions)

---

**Made with ❤️ by the Browse-to-Test community** 