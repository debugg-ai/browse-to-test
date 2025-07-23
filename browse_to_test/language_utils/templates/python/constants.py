#!/usr/bin/env python3
"""
Test constants and configuration values for Python test scripts.
"""

# Default timeouts (in milliseconds)
DEFAULT_TIMEOUT = 10000
PAGE_LOAD_TIMEOUT = 30000
ELEMENT_TIMEOUT = 10000
ACTION_TIMEOUT = 5000

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 1000  # milliseconds

# Browser settings
DEFAULT_BROWSER = "chromium"
HEADLESS_MODE = False
SLOW_MO = 0  # milliseconds

# Viewport settings
DEFAULT_VIEWPORT = {
    "width": 1280,
    "height": 720
}

# Screenshot settings
SCREENSHOT_ON_FAILURE = True
SCREENSHOT_PATH = "./screenshots"

# Wait conditions
WAIT_CONDITIONS = {
    "visible": "visible",
    "hidden": "hidden", 
    "attached": "attached",
    "detached": "detached"
}

# Common selectors
COMMON_SELECTORS = {
    "submit_button": "button[type='submit'], input[type='submit']",
    "text_input": "input[type='text'], input[type='email'], input[type='password']",
    "link": "a[href]",
    "form": "form",
    "modal": ".modal, [role='dialog']",
    "close_button": ".close, [aria-label*='close'], [aria-label*='Close']"
}

# Test data patterns
SENSITIVE_DATA_PATTERNS = [
    "password",
    "secret", 
    "token",
    "key",
    "credential",
    "auth",
    "api_key",
    "access_token"
]

# Framework-specific constants

# Playwright constants
PLAYWRIGHT_ACTIONS = {
    "click": "click",
    "fill": "fill", 
    "select": "select_option",
    "check": "check",
    "uncheck": "uncheck",
    "hover": "hover",
    "focus": "focus",
    "blur": "blur"
}

PLAYWRIGHT_ASSERTIONS = {
    "visible": "to_be_visible",
    "hidden": "to_be_hidden",
    "enabled": "to_be_enabled", 
    "disabled": "to_be_disabled",
    "checked": "to_be_checked",
    "unchecked": "not.to_be_checked"
}

# Selenium constants  
SELENIUM_BY_TYPES = {
    "id": "ID",
    "name": "NAME",
    "xpath": "XPATH", 
    "css": "CSS_SELECTOR",
    "class": "CLASS_NAME",
    "tag": "TAG_NAME",
    "link_text": "LINK_TEXT",
    "partial_link_text": "PARTIAL_LINK_TEXT"
}

SELENIUM_ACTIONS = {
    "click": "click",
    "send_keys": "send_keys",
    "clear": "clear",
    "submit": "submit"
}

# Error messages
ERROR_MESSAGES = {
    "element_not_found": "Element not found: {selector}",
    "timeout": "Action timed out after {timeout}ms: {action}",
    "action_failed": "Action failed: {action} on {selector}",
    "page_load_failed": "Page failed to load: {url}",
    "assertion_failed": "Assertion failed: {assertion} for {selector}"
}

# Success messages
SUCCESS_MESSAGES = {
    "action_completed": "Successfully completed: {action} on {selector}",
    "page_loaded": "Page loaded successfully: {url}",
    "assertion_passed": "Assertion passed: {assertion} for {selector}",
    "test_completed": "Test completed successfully"
}

# Test configuration
TEST_CONFIG = {
    "browser_args": [
        "--no-sandbox",
        "--disable-web-security",
        "--disable-dev-shm-usage",
        "--disable-gpu"
    ],
    "ignore_https_errors": True,
    "color_scheme": "light",
    "locale": "en-US",
    "timezone": "UTC"
} 