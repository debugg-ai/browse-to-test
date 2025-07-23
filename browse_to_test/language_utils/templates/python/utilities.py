#!/usr/bin/env python3
"""
Unified test utilities for Python test scripts.

This file contains reusable helper functions, exception classes,
and utilities that can be imported by generated test scripts.
"""

import sys
import asyncio
from typing import Dict, Any, Optional, Union, List
from contextlib import asynccontextmanager


# Custom exception classes

class TestActionError(Exception):
    """Exception raised when a test action fails."""
    pass


class ElementNotFoundError(TestActionError):
    """Exception raised when an element cannot be found."""
    pass


class TimeoutError(TestActionError):
    """Exception raised when an action times out."""
    pass


# Framework-agnostic utilities

def log_step(step: str, details: str = ""):
    """Log a test step with optional details."""
    print(f"🔸 {step}", file=sys.stderr)
    if details:
        print(f"   {details}", file=sys.stderr)


def log_error(error: str, details: str = ""):
    """Log an error with optional details.""" 
    print(f"❌ {error}", file=sys.stderr)
    if details:
        print(f"   {details}", file=sys.stderr)


def log_success(message: str):
    """Log a success message."""
    print(f"✅ {message}", file=sys.stderr)


# Playwright-specific utilities

async def safe_playwright_action(page, action_func, *args, step_info: str = '', **kwargs):
    """Execute a Playwright action with error handling."""
    try:
        log_step(f"Executing action: {action_func.__name__}", step_info)
        return await action_func(*args, **kwargs)
    except Exception as e:
        error_msg = f"Playwright action failed ({action_func.__name__}): {e}"
        log_error(error_msg, step_info)
        raise TestActionError(error_msg) from e


async def try_locate_and_act_playwright(page, selector: str, action_type: str, text: str = None, step_info: str = '', timeout: int = 10000):
    """Locate element and perform action with fallback selectors."""
    log_step(f"Attempting {action_type} using selector: {selector}", step_info)
    
    try:
        locator = page.locator(selector).first
        
        if action_type == 'click':
            await locator.click(timeout=timeout)
            log_success(f"Successfully clicked element: {selector}")
        elif action_type == 'fill' and text is not None:
            await locator.fill(text, timeout=timeout)
            log_success(f"Successfully filled element: {selector}")
        elif action_type == 'select' and text is not None:
            await locator.select_option(value=text, timeout=timeout)
            log_success(f"Successfully selected option: {text}")
        else:
            raise ValueError(f'Unknown action type: {action_type}')
            
    except Exception as e:
        error_msg = f"Failed to {action_type} element {selector}: {e}"
        log_error(error_msg, step_info)
        raise ElementNotFoundError(error_msg) from e


async def assert_element_visible_playwright(page, selector: str, timeout: int = 10000):
    """Assert that an element is visible on the page."""
    try:
        log_step(f"Asserting element is visible: {selector}")
        element = page.locator(selector).first
        await element.wait_for(state="visible", timeout=timeout)
        log_success(f"Element is visible: {selector}")
    except Exception as e:
        error_msg = f"Element not visible: {selector} - {e}"
        log_error(error_msg)
        raise ElementNotFoundError(error_msg) from e


async def wait_for_page_load_playwright(page, timeout: int = 30000):
    """Wait for page to fully load."""
    try:
        log_step("Waiting for page load")
        await page.wait_for_load_state("networkidle", timeout=timeout)
        log_success("Page loaded successfully")
    except Exception as e:
        error_msg = f"Page load timeout: {e}"
        log_error(error_msg)
        raise TimeoutError(error_msg) from e


# Selenium-specific utilities

def safe_selenium_action(driver, action_func, *args, step_info: str = '', **kwargs):
    """Execute a Selenium action with error handling."""
    try:
        log_step(f"Executing action: {action_func.__name__}", step_info)
        return action_func(*args, **kwargs)
    except Exception as e:
        error_msg = f"Selenium action failed ({action_func.__name__}): {e}"
        log_error(error_msg, step_info)
        raise TestActionError(error_msg) from e


def try_locate_and_act_selenium(driver, selector: str, by_type: str, action_type: str, text: str = None, step_info: str = '', timeout: int = 10):
    """Locate element and perform action with Selenium."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import Select
    
    log_step(f"Attempting {action_type} using {by_type}: {selector}", step_info)
    
    try:
        # Map by_type string to By constants
        by_mapping = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by_locator = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by_locator, selector)))
        
        if action_type == 'click':
            element.click()
            log_success(f"Successfully clicked element: {selector}")
        elif action_type == 'send_keys' and text is not None:
            element.clear()
            element.send_keys(text)
            log_success(f"Successfully sent keys to element: {selector}")
        elif action_type == 'select' and text is not None:
            select = Select(element)
            select.select_by_visible_text(text)
            log_success(f"Successfully selected option: {text}")
        else:
            raise ValueError(f'Unknown action type: {action_type}')
            
    except Exception as e:
        error_msg = f"Failed to {action_type} element {selector}: {e}"
        log_error(error_msg, step_info)
        raise ElementNotFoundError(error_msg) from e


def assert_element_visible_selenium(driver, selector: str, by_type: str = 'css', timeout: int = 10):
    """Assert that an element is visible with Selenium."""
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        log_step(f"Asserting element is visible: {selector}")
        
        by_mapping = {
            'id': By.ID,
            'name': By.NAME,
            'xpath': By.XPATH,
            'css': By.CSS_SELECTOR,
            'class': By.CLASS_NAME,
            'tag': By.TAG_NAME
        }
        
        by_locator = by_mapping.get(by_type.lower(), By.CSS_SELECTOR)
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.visibility_of_element_located((by_locator, selector)))
        log_success(f"Element is visible: {selector}")
        return element
    except Exception as e:
        error_msg = f"Element not visible: {selector} - {e}"
        log_error(error_msg)
        raise ElementNotFoundError(error_msg) from e


# Data handling utilities

def mask_sensitive_data(data: Any, sensitive_keys: List[str] = None) -> Any:
    """Mask sensitive data in test data."""
    if sensitive_keys is None:
        sensitive_keys = ['password', 'token', 'key', 'secret', 'credential']
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(sensitive_key.lower() in key.lower() for sensitive_key in sensitive_keys):
                masked[key] = '***MASKED***'
            else:
                masked[key] = mask_sensitive_data(value, sensitive_keys)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, sensitive_keys) for item in data]
    else:
        return data


def generate_test_data(template: Dict[str, Any], **overrides) -> Dict[str, Any]:
    """Generate test data from template with overrides."""
    test_data = template.copy()
    test_data.update(overrides)
    return test_data 