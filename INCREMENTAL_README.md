# Incremental Test Script Generation

This document describes the new **live update** functionality in browse-to-test that allows for real-time test script generation as browser automation steps are performed.

## Overview

The incremental system enables a three-phase approach to test generation:

1. **Setup Phase**: Initialize script structure, imports, browser context
2. **Incremental Phase**: Add test steps one at a time as they come in
3. **Finalization Phase**: Complete the script, validate, and optimize

This approach is ideal for scenarios where you want to generate test scripts live during browser automation recording or when processing steps from a real-time stream.

## Quick Start

### Basic Usage

```python
import asyncio
from browse_to_test import (
    start_incremental_session,
    add_incremental_step,
    finalize_incremental_session
)

async def main():
    # Start an incremental session
    orchestrator, setup = start_incremental_session(
        output_framework="playwright",
        target_url="https://example.com"
    )
    
    if setup.success:
        # Add steps as they come in
        step_data = {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            },
            "state": {"interacted_element": []}
        }
        
        result = orchestrator.add_step(step_data)
        print(f"Added step: {result.success}")
        
        # Finalize when done
        final = orchestrator.finalize_session()
        if final.success:
            print("Generated script:")
            print(final.updated_script)

asyncio.run(main())
```

### Advanced Usage with Configuration

```python
from browse_to_test import IncrementalE2eScriptOrchestrator, Config

# Create custom configuration
config = Config(
    output=OutputConfig(
        framework="playwright",
        include_assertions=True,
        include_error_handling=True,
        sensitive_data_keys=["username", "password"]
    ),
    processing=ProcessingConfig(
        analyze_actions_with_ai=True,  # Enable AI analysis
        collect_system_context=True
    )
)

# Create orchestrator
orchestrator = IncrementalE2eScriptOrchestrator(config)

# Start session with context hints
setup = orchestrator.start_incremental_session(
    target_url="https://app.example.com/login",
    context_hints={
        "flow_type": "authentication",
        "critical_elements": ["username", "password", "submit"]
    }
)
```

## Live Update Callbacks

Monitor progress with real-time callbacks:

```python
def update_callback(result):
    print(f"Update: +{result.new_lines_added} lines")
    if result.validation_issues:
        print(f"Issues: {result.validation_issues}")
    if result.analysis_insights:
        print(f"Insights: {result.analysis_insights}")

orchestrator.register_update_callback(update_callback)
```

## Supported Frameworks

### Playwright (Incremental)
- **Plugin**: `IncrementalPlaywrightPlugin`
- **Features**: Full incremental support, async/await syntax
- **Validations**: Page interactions, browser cleanup, timing issues
- **Optimizations**: Network interception, selector recommendations

### Selenium (Incremental)  
- **Plugin**: `IncrementalSeleniumPlugin`
- **Features**: Full incremental support, unittest structure
- **Validations**: WebDriver interactions, proper test structure
- **Optimizations**: Explicit waits, Page Object Pattern suggestions

## API Reference

### `start_incremental_session()`

Start a new incremental session.

```python
orchestrator, setup_result = start_incremental_session(
    output_framework="playwright",    # Framework to use
    target_url="https://example.com", # Target URL (optional)
    config={...},                     # Configuration overrides
    context_hints={...}               # Context hints for AI
)
```

**Returns**: Tuple of `(orchestrator, setup_result)`

### `add_incremental_step()`

Add a step to the active session.

```python
result = add_incremental_step(
    orchestrator,     # Active orchestrator
    step_data,        # Step data dictionary
    analyze_step=True # Whether to perform AI analysis
)
```

**Returns**: `IncrementalUpdateResult`

### `finalize_incremental_session()`

Finalize the session and get the complete script.

```python
final_result = finalize_incremental_session(
    orchestrator,          # Active orchestrator
    final_validation=True, # Perform final validation
    optimize_script=True   # Apply optimizations
)
```

**Returns**: `IncrementalUpdateResult` with final script

### `IncrementalUpdateResult`

Result object containing:
- `success`: Whether the operation succeeded
- `updated_script`: Current complete script
- `new_lines_added`: Number of lines added in this update  
- `validation_issues`: List of validation issues found
- `analysis_insights`: List of AI analysis insights
- `metadata`: Additional metadata about the update

### `ScriptState`

Internal state tracking:
- `imports`: Import statements
- `helpers`: Helper functions
- `setup_code`: Browser setup code
- `test_steps`: Generated test steps
- `cleanup_code`: Cleanup code
- `current_step_count`: Number of steps processed
- `total_actions`: Total actions processed
- `setup_complete`: Whether setup is complete
- `finalized`: Whether session is finalized

## Error Handling

The incremental system provides robust error handling:

```python
# Graceful handling of invalid data
result = orchestrator.add_step(invalid_data)
if not result.success:
    print(f"Errors: {result.validation_issues}")

# Session state validation
try:
    orchestrator.start_incremental_session()
    orchestrator.start_incremental_session()  # Will raise RuntimeError
except RuntimeError as e:
    print(f"Session error: {e}")

# Automatic cleanup on errors
try:
    # ... incremental operations
except Exception:
    orchestrator.abort_session()  # Clean up resources
```

## Configuration

### Output Configuration
```python
OutputConfig(
    framework="playwright",        # Target framework
    language="python",             # Output language
    include_assertions=True,       # Include test assertions
    include_error_handling=True,   # Include error handling
    include_logging=True,          # Include logging statements
    mask_sensitive_data=True,      # Mask sensitive data
    sensitive_data_keys=["password"] # Keys to mask
)
```

### Processing Configuration
```python
ProcessingConfig(
    analyze_actions_with_ai=True,     # Enable AI analysis
    collect_system_context=True,      # Collect project context
    use_intelligent_analysis=True,    # Use advanced AI features
    strict_mode=False                 # Strict validation mode
)
```

## Examples

### Login Flow Example

```python
login_steps = [
    {
        "model_output": {
            "action": [{"go_to_url": {"url": "https://example.com/login"}}]
        },
        "state": {"interacted_element": []},
        "metadata": {"description": "Navigate to login"}
    },
    {
        "model_output": {
            "action": [{"input_text": {"text": "user@example.com", "index": 0}}]
        },
        "state": {
            "interacted_element": [{
                "css_selector": "input[data-testid='username']",
                "attributes": {"data-testid": "username", "type": "email"}
            }]
        },
        "metadata": {"description": "Enter username"}
    },
    # ... more steps
]

# Process incrementally
orchestrator, setup = start_incremental_session("playwright")
for step in login_steps:
    result = orchestrator.add_step(step)
    print(f"Step processed: {result.success}")

final = orchestrator.finalize_session()
```

### E-commerce Flow Example

```python
shopping_steps = [
    # Navigation
    {"model_output": {"action": [{"go_to_url": {"url": "https://shop.example.com"}}]}},
    
    # Search
    {"model_output": {"action": [{"input_text": {"text": "laptop", "index": 0}}]}},
    
    # Click search
    {"model_output": {"action": [{"click_element": {"index": 0}}]}},
    
    # Add to cart
    {"model_output": {"action": [{"click_element": {"index": 0}}]}},
]

# Process with context hints
orchestrator, setup = start_incremental_session(
    "playwright",
    target_url="https://shop.example.com",
    context_hints={
        "flow_type": "e_commerce",
        "critical_elements": ["search", "add-to-cart"]
    }
)
```

## Running Examples

Try the included examples:

```bash
# Basic incremental demo
python examples/incremental_demo.py

# Full test flows
python examples/incremental_test_flows.py

# Run tests
pytest tests/test_incremental_orchestrator.py
```

## Benefits

1. **Real-time Generation**: See test scripts build up as actions are performed
2. **Early Validation**: Catch issues immediately rather than at the end
3. **Progress Tracking**: Monitor step-by-step progress with callbacks
4. **Memory Efficient**: Process steps individually rather than batching
5. **Flexible Architecture**: Easy to integrate with live automation systems
6. **Robust Error Handling**: Graceful handling of invalid or incomplete data

## Migration from Batch Mode

Existing batch code:
```python
# Old batch approach
script = convert_to_test_script(automation_data, "playwright")
```

New incremental approach:
```python
# New incremental approach
orchestrator, setup = start_incremental_session("playwright")
for step in automation_data:
    orchestrator.add_step(step)
final = orchestrator.finalize_session()
script = final.updated_script
```

The incremental system is fully compatible with existing data formats and provides the same output quality with enhanced real-time capabilities. 