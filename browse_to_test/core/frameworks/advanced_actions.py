#!/usr/bin/env python3
"""
Advanced Action Support System for Browse-to-Test

This module extends the basic action set with complex browser interactions:
- Drag and drop operations
- File uploads and downloads
- Keyboard shortcuts and combinations
- Mobile touch gestures
- Modern web interactions (hover, double-click, right-click)
- Clipboard operations
- Multi-tab/window handling
- Screenshot and visual comparisons
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from pathlib import Path


class AdvancedActionType(Enum):
    """Types of advanced actions supported."""
    # Drag and Drop
    DRAG_AND_DROP = "drag_and_drop"
    DRAG_TO_POSITION = "drag_to_position"
    
    # File Operations
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    
    # Keyboard Operations
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    KEY_COMBINATION = "key_combination"
    
    # Mouse Operations
    HOVER = "hover"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    
    # Mobile Gestures
    SWIPE = "swipe"
    PINCH_ZOOM = "pinch_zoom"
    TOUCH_HOLD = "touch_hold"
    
    # Web Interactions
    SCROLL_INTO_VIEW = "scroll_into_view"
    SCROLL_TO_ELEMENT = "scroll_to_element"
    
    # Browser Operations
    NEW_TAB = "new_tab"
    SWITCH_TAB = "switch_tab"
    CLOSE_TAB = "close_tab"
    NEW_WINDOW = "new_window"
    
    # Clipboard Operations
    COPY_TEXT = "copy_text"
    PASTE_TEXT = "paste_text"
    
    # Visual Operations
    TAKE_SCREENSHOT = "take_screenshot"
    VISUAL_COMPARISON = "visual_comparison"
    
    # Form Interactions
    SELECT_DROPDOWN = "select_dropdown"
    CHECK_CHECKBOX = "check_checkbox"
    RADIO_SELECT = "radio_select"
    
    # Media Interactions
    PLAY_VIDEO = "play_video"
    PAUSE_VIDEO = "pause_video"
    SET_VOLUME = "set_volume"


@dataclass
class DragDropConfig:
    """Configuration for drag and drop operations."""
    source_selector: str
    target_selector: str
    drag_duration: int = 1000  # milliseconds
    steps: int = 5  # Number of intermediate steps
    offset_x: int = 0  # Target offset X
    offset_y: int = 0  # Target offset Y
    hold_delay: int = 100  # Delay before starting drag
    release_delay: int = 100  # Delay before releasing


@dataclass
class FileUploadConfig:
    """Configuration for file upload operations."""
    file_path: str
    file_input_selector: str
    wait_for_upload: bool = True
    upload_timeout: int = 30000
    verify_upload: bool = True
    expected_filename: Optional[str] = None


@dataclass
class KeyboardConfig:
    """Configuration for keyboard operations."""
    keys: List[str]
    modifier_keys: List[str] = field(default_factory=list)  # Ctrl, Alt, Shift, Meta
    delay_between_keys: int = 50
    hold_duration: int = 100


@dataclass
class MobileGestureConfig:
    """Configuration for mobile gestures."""
    start_x: int
    start_y: int
    end_x: Optional[int] = None
    end_y: Optional[int] = None
    duration: int = 1000
    velocity: float = 1.0
    scale: float = 1.0  # For pinch zoom
    rotation: float = 0.0  # For rotation gestures


@dataclass
class VisualComparisonConfig:
    """Configuration for visual comparisons."""
    baseline_image: str
    threshold: float = 0.1  # Similarity threshold (0-1)
    ignore_areas: List[Dict[str, int]] = field(default_factory=list)  # Areas to ignore
    full_page: bool = False
    element_selector: Optional[str] = None


class AdvancedActionGenerator:
    """Generates code for advanced browser actions."""
    
    def __init__(self, framework: str = "playwright", language: str = "python"):
        self.framework = framework
        self.language = language
        self.action_generators = self._initialize_generators()
    
    def _initialize_generators(self) -> Dict[str, callable]:
        """Initialize action generators for different frameworks."""
        if self.framework == "playwright":
            return {
                AdvancedActionType.DRAG_AND_DROP.value: self._generate_playwright_drag_drop,
                AdvancedActionType.FILE_UPLOAD.value: self._generate_playwright_file_upload,
                AdvancedActionType.KEYBOARD_SHORTCUT.value: self._generate_playwright_keyboard,
                AdvancedActionType.HOVER.value: self._generate_playwright_hover,
                AdvancedActionType.DOUBLE_CLICK.value: self._generate_playwright_double_click,
                AdvancedActionType.RIGHT_CLICK.value: self._generate_playwright_right_click,
                AdvancedActionType.SWIPE.value: self._generate_playwright_swipe,
                AdvancedActionType.SCREENSHOT.value: self._generate_playwright_screenshot,
                AdvancedActionType.NEW_TAB.value: self._generate_playwright_new_tab,
                AdvancedActionType.SELECT_DROPDOWN.value: self._generate_playwright_select,
            }
        elif self.framework == "selenium":
            return {
                AdvancedActionType.DRAG_AND_DROP.value: self._generate_selenium_drag_drop,
                AdvancedActionType.FILE_UPLOAD.value: self._generate_selenium_file_upload,
                AdvancedActionType.KEYBOARD_SHORTCUT.value: self._generate_selenium_keyboard,
                AdvancedActionType.HOVER.value: self._generate_selenium_hover,
                AdvancedActionType.DOUBLE_CLICK.value: self._generate_selenium_double_click,
                AdvancedActionType.RIGHT_CLICK.value: self._generate_selenium_right_click,
                AdvancedActionType.SCREENSHOT.value: self._generate_selenium_screenshot,
                AdvancedActionType.NEW_TAB.value: self._generate_selenium_new_tab,
                AdvancedActionType.SELECT_DROPDOWN.value: self._generate_selenium_select,
            }
        else:
            return {}
    
    def generate_action(self, action_type: str, config: Dict[str, Any],
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate code for an advanced action.
        
        Args:
            action_type: Type of advanced action
            config: Action configuration
            context: Additional context
            
        Returns:
            Generated action code and metadata
        """
        generator = self.action_generators.get(action_type)
        if not generator:
            raise ValueError(f"Unsupported action type: {action_type} for framework: {self.framework}")
        
        return generator(config, context)
    
    # Playwright Action Generators
    
    def _generate_playwright_drag_drop(self, config: Dict[str, Any], 
                                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright drag and drop code."""
        drag_config = DragDropConfig(**config)
        
        if self.language == "python":
            code = f'''
# Drag and drop operation
source_element = page.locator("{drag_config.source_selector}")
target_element = page.locator("{drag_config.target_selector}")

# Wait for elements to be ready
await source_element.wait_for(state="visible", timeout=30000)
await target_element.wait_for(state="visible", timeout=30000)

# Perform drag and drop with custom options
await source_element.drag_to(
    target_element,
    source_position={{"x": 0, "y": 0}},
    target_position={{"x": {drag_config.offset_x}, "y": {drag_config.offset_y}}},
    timeout=30000
)

# Alternative: Manual drag and drop for more control
# source_box = await source_element.bounding_box()
# target_box = await target_element.bounding_box()
# 
# await page.mouse.move(source_box["x"] + source_box["width"]/2, 
#                      source_box["y"] + source_box["height"]/2)
# await page.mouse.down()
# await page.mouse.move(target_box["x"] + target_box["width"]/2, 
#                      target_box["y"] + target_box["height"]/2,
#                      steps={drag_config.steps})
# await page.mouse.up()
'''
        elif self.language == "typescript":
            code = f'''
// Drag and drop operation
const sourceElement = page.locator("{drag_config.source_selector}");
const targetElement = page.locator("{drag_config.target_selector}");

// Wait for elements to be ready
await sourceElement.waitFor({{ state: "visible", timeout: 30000 }});
await targetElement.waitFor({{ state: "visible", timeout: 30000 }});

// Perform drag and drop
await sourceElement.dragTo(targetElement, {{
    sourcePosition: {{ x: 0, y: 0 }},
    targetPosition: {{ x: {drag_config.offset_x}, y: {drag_config.offset_y} }},
    timeout: 30000
}});
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "assertions": [
                f'await expect(target_element).toBeVisible()',
                f'# Verify drag and drop completed successfully'
            ],
            "waits": [
                f'await source_element.wait_for(state="visible")',
                f'await target_element.wait_for(state="visible")'
            ]
        }
    
    def _generate_playwright_file_upload(self, config: Dict[str, Any],
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright file upload code."""
        upload_config = FileUploadConfig(**config)
        
        if self.language == "python":
            code = f'''
# File upload operation
file_input = page.locator("{upload_config.file_input_selector}")

# Wait for file input to be ready
await file_input.wait_for(state="attached", timeout=30000)

# Upload file
await file_input.set_input_files("{upload_config.file_path}")

# Verify upload if enabled
'''
            if upload_config.verify_upload and upload_config.expected_filename:
                code += f'''
# Wait for upload confirmation
upload_indicator = page.locator(f'text="{upload_config.expected_filename}"')
await upload_indicator.wait_for(state="visible", timeout={upload_config.upload_timeout})
'''
        
        elif self.language == "typescript":
            code = f'''
// File upload operation
const fileInput = page.locator("{upload_config.file_input_selector}");

// Wait for file input to be ready
await fileInput.waitFor({{ state: "attached", timeout: 30000 }});

// Upload file
await fileInput.setInputFiles("{upload_config.file_path}");
'''
            if upload_config.verify_upload and upload_config.expected_filename:
                code += f'''
// Wait for upload confirmation
const uploadIndicator = page.locator('text="{upload_config.expected_filename}"');
await uploadIndicator.waitFor({{ state: "visible", timeout: {upload_config.upload_timeout} }});
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "file_dependencies": [upload_config.file_path],
            "assertions": [
                f'await expect(file_input).toHaveValue(/{upload_config.expected_filename or ".*"}/)'
            ] if upload_config.verify_upload else []
        }
    
    def _generate_playwright_keyboard(self, config: Dict[str, Any],
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright keyboard shortcut code."""
        keyboard_config = KeyboardConfig(**config)
        
        # Build key combination
        key_combination = "+".join(keyboard_config.modifier_keys + keyboard_config.keys)
        
        if self.language == "python":
            code = f'''
# Keyboard shortcut: {key_combination}
await page.keyboard.press("{key_combination}")

# Alternative: Individual key presses with delays
'''
            if keyboard_config.delay_between_keys > 0:
                code += f'''
# Press keys individually with delays
'''
                for modifier in keyboard_config.modifier_keys:
                    code += f'await page.keyboard.down("{modifier}")\n'
                    if keyboard_config.delay_between_keys:
                        code += f'await page.wait_for_timeout({keyboard_config.delay_between_keys})\n'
                
                for key in keyboard_config.keys:
                    code += f'await page.keyboard.press("{key}")\n'
                    if keyboard_config.delay_between_keys:
                        code += f'await page.wait_for_timeout({keyboard_config.delay_between_keys})\n'
                
                for modifier in reversed(keyboard_config.modifier_keys):
                    code += f'await page.keyboard.up("{modifier}")\n'
        
        elif self.language == "typescript":
            code = f'''
// Keyboard shortcut: {key_combination}
await page.keyboard.press("{key_combination}");
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "metadata": {
                "key_combination": key_combination,
                "modifier_keys": keyboard_config.modifier_keys,
                "keys": keyboard_config.keys
            }
        }
    
    def _generate_playwright_hover(self, config: Dict[str, Any],
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright hover action."""
        selector = config.get("selector", "")
        
        if self.language == "python":
            code = f'''
# Hover over element
element = page.locator("{selector}")
await element.wait_for(state="visible", timeout=30000)
await element.hover()

# Optional: Hover with specific position
# await element.hover(position={{"x": 10, "y": 10}})
'''
        elif self.language == "typescript":
            code = f'''
// Hover over element
const element = page.locator("{selector}");
await element.waitFor({{ state: "visible", timeout: 30000 }});
await element.hover();
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "waits": [f'await element.wait_for(state="visible")']
        }
    
    def _generate_playwright_double_click(self, config: Dict[str, Any],
                                        context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright double click action."""
        selector = config.get("selector", "")
        
        if self.language == "python":
            code = f'''
# Double click element
element = page.locator("{selector}")
await element.wait_for(state="visible", timeout=30000)
await element.dblclick()
'''
        elif self.language == "typescript":
            code = f'''
// Double click element  
const element = page.locator("{selector}");
await element.waitFor({{ state: "visible", timeout: 30000 }});
await element.dblclick();
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "waits": [f'await element.wait_for(state="visible")']
        }
    
    def _generate_playwright_right_click(self, config: Dict[str, Any],
                                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright right click action."""
        selector = config.get("selector", "")
        
        if self.language == "python":
            code = f'''
# Right click element
element = page.locator("{selector}")
await element.wait_for(state="visible", timeout=30000)
await element.click(button="right")
'''
        elif self.language == "typescript":
            code = f'''
// Right click element
const element = page.locator("{selector}");
await element.waitFor({{ state: "visible", timeout: 30000 }});
await element.click({{ button: "right" }});
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "waits": [f'await element.wait_for(state="visible")']
        }
    
    def _generate_playwright_swipe(self, config: Dict[str, Any],
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright mobile swipe action."""
        gesture_config = MobileGestureConfig(**config)
        
        if self.language == "python":
            code = f'''
# Mobile swipe gesture
await page.mouse.move({gesture_config.start_x}, {gesture_config.start_y})
await page.mouse.down()
await page.mouse.move({gesture_config.end_x}, {gesture_config.end_y}, 
                     steps=10)  # Smooth swipe with multiple steps
await page.mouse.up()

# Alternative: Using touch actions (requires mobile context)
# await page.touchscreen.tap({gesture_config.start_x}, {gesture_config.start_y})
'''
        elif self.language == "typescript":
            code = f'''
// Mobile swipe gesture
await page.mouse.move({gesture_config.start_x}, {gesture_config.start_y});
await page.mouse.down();
await page.mouse.move({gesture_config.end_x}, {gesture_config.end_y}, {{ steps: 10 }});
await page.mouse.up();
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "metadata": {
                "gesture_type": "swipe",
                "start_position": (gesture_config.start_x, gesture_config.start_y),
                "end_position": (gesture_config.end_x, gesture_config.end_y)
            }
        }
    
    def _generate_playwright_screenshot(self, config: Dict[str, Any],
                                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright screenshot action."""
        filename = config.get("filename", "screenshot.png")
        full_page = config.get("full_page", False)
        element_selector = config.get("element_selector")
        
        if self.language == "python":
            if element_selector:
                code = f'''
# Take element screenshot
element = page.locator("{element_selector}")
await element.wait_for(state="visible", timeout=30000)
await element.screenshot(path="{filename}")
'''
            else:
                code = f'''
# Take page screenshot
await page.screenshot(path="{filename}", full_page={str(full_page).lower()})
'''
        elif self.language == "typescript":
            if element_selector:
                code = f'''
// Take element screenshot
const element = page.locator("{element_selector}");
await element.waitFor({{ state: "visible", timeout: 30000 }});
await element.screenshot({{ path: "{filename}" }});
'''
            else:
                code = f'''
// Take page screenshot
await page.screenshot({{ path: "{filename}", fullPage: {str(full_page).lower()} }});
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "file_outputs": [filename],
            "waits": [f'await element.wait_for(state="visible")'] if element_selector else []
        }
    
    def _generate_playwright_new_tab(self, config: Dict[str, Any],
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright new tab action."""
        url = config.get("url", "about:blank")
        
        if self.language == "python":
            code = f'''
# Open new tab
new_page = await context.new_page()
await new_page.goto("{url}")

# Switch to new tab (new_page is now active)
# To switch back to original tab, use: await page.bring_to_front()
'''
        elif self.language == "typescript":
            code = f'''
// Open new tab
const newPage = await context.newPage();
await newPage.goto("{url}");
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "metadata": {
                "action_type": "new_tab",
                "target_url": url
            }
        }
    
    def _generate_playwright_select(self, config: Dict[str, Any],
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Playwright dropdown selection."""
        selector = config.get("selector", "")
        value = config.get("value", "")
        by = config.get("by", "value")  # value, label, index
        
        if self.language == "python":
            if by == "value":
                code = f'''
# Select dropdown option by value
dropdown = page.locator("{selector}")
await dropdown.wait_for(state="visible", timeout=30000)
await dropdown.select_option(value="{value}")
'''
            elif by == "label":
                code = f'''
# Select dropdown option by label
dropdown = page.locator("{selector}")
await dropdown.wait_for(state="visible", timeout=30000)
await dropdown.select_option(label="{value}")
'''
            elif by == "index":
                code = f'''
# Select dropdown option by index
dropdown = page.locator("{selector}")
await dropdown.wait_for(state="visible", timeout=30000)
await dropdown.select_option(index={value})
'''
        elif self.language == "typescript":
            if by == "value":
                code = f'''
// Select dropdown option by value
const dropdown = page.locator("{selector}");
await dropdown.waitFor({{ state: "visible", timeout: 30000 }});
await dropdown.selectOption({{ value: "{value}" }});
'''
            elif by == "label":
                code = f'''
// Select dropdown option by label
const dropdown = page.locator("{selector}");
await dropdown.waitFor({{ state: "visible", timeout: 30000 }});
await dropdown.selectOption({{ label: "{value}" }});
'''
            elif by == "index":
                code = f'''
// Select dropdown option by index
const dropdown = page.locator("{selector}");
await dropdown.waitFor({{ state: "visible", timeout: 30000 }});
await dropdown.selectOption({{ index: {value} }});
'''
        
        return {
            "code": code,
            "imports": self._get_playwright_imports(),
            "waits": [f'await dropdown.wait_for(state="visible")'],
            "assertions": [f'await expect(dropdown).toHaveValue("{value}")'] if by == "value" else []
        }
    
    # Selenium Action Generators
    
    def _generate_selenium_drag_drop(self, config: Dict[str, Any],
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium drag and drop code."""
        drag_config = DragDropConfig(**config)
        
        if self.language == "python":
            code = f'''
# Drag and drop operation
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Find elements
source_element = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "{drag_config.source_selector}"))
)
target_element = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "{drag_config.target_selector}"))
)

# Perform drag and drop
actions = ActionChains(driver)
actions.drag_and_drop(source_element, target_element).perform()

# Alternative with offset
# actions.drag_and_drop_by_offset(source_element, {drag_config.offset_x}, {drag_config.offset_y}).perform()
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports() + [
                "from selenium.webdriver.common.action_chains import ActionChains"
            ],
            "waits": [
                f'WebDriverWait(driver, 30).until(EC.element_to_be_clickable(source_selector))',
                f'WebDriverWait(driver, 30).until(EC.visibility_of_element_located(target_selector))'
            ]
        }
    
    def _generate_selenium_file_upload(self, config: Dict[str, Any],
                                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium file upload code."""
        upload_config = FileUploadConfig(**config)
        
        if self.language == "python":
            code = f'''
# File upload operation
file_input = WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "{upload_config.file_input_selector}"))
)

# Upload file
file_input.send_keys("{upload_config.file_path}")
'''
            if upload_config.verify_upload and upload_config.expected_filename:
                code += f'''
# Verify upload
upload_indicator = WebDriverWait(driver, {upload_config.upload_timeout // 1000}).until(
    EC.visibility_of_element_located((By.XPATH, f'//text()[contains(., "{upload_config.expected_filename}")]'))
)
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports(),
            "file_dependencies": [upload_config.file_path]
        }
    
    def _generate_selenium_keyboard(self, config: Dict[str, Any],
                                  context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium keyboard shortcut code."""
        keyboard_config = KeyboardConfig(**config)
        
        # Map modifier keys to Selenium keys
        key_mapping = {
            "ctrl": "Keys.CONTROL",
            "alt": "Keys.ALT", 
            "shift": "Keys.SHIFT",
            "meta": "Keys.META",
            "cmd": "Keys.COMMAND"
        }
        
        selenium_modifiers = [key_mapping.get(key.lower(), f'"{key}"') for key in keyboard_config.modifier_keys]
        selenium_keys = [f'"{key}"' for key in keyboard_config.keys]
        
        if self.language == "python":
            code = f'''
# Keyboard shortcut
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

actions = ActionChains(driver)
'''
            # Build key combination
            all_keys = selenium_modifiers + selenium_keys
            if len(all_keys) == 1:
                code += f'actions.send_keys({all_keys[0]}).perform()'
            else:
                key_combination = " + ".join(all_keys)
                code += f'''
# Press key combination: {" + ".join(keyboard_config.modifier_keys + keyboard_config.keys)}
actions.key_down({selenium_modifiers[0] if selenium_modifiers else selenium_keys[0]})
'''
                for key in (selenium_modifiers[1:] + selenium_keys):
                    code += f'actions.key_down({key})\n'
                for key in reversed(selenium_modifiers + selenium_keys):
                    code += f'actions.key_up({key})\n'
                code += 'actions.perform()'
        
        return {
            "code": code,
            "imports": self._get_selenium_imports() + [
                "from selenium.webdriver.common.keys import Keys",
                "from selenium.webdriver.common.action_chains import ActionChains"
            ]
        }
    
    def _generate_selenium_hover(self, config: Dict[str, Any],
                               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium hover action."""
        selector = config.get("selector", "")
        
        if self.language == "python":
            code = f'''
# Hover over element
from selenium.webdriver.common.action_chains import ActionChains

element = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "{selector}"))
)

actions = ActionChains(driver)
actions.move_to_element(element).perform()
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports() + [
                "from selenium.webdriver.common.action_chains import ActionChains"
            ]
        }
    
    def _generate_selenium_double_click(self, config: Dict[str, Any],
                                      context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium double click action."""
        selector = config.get("selector", "")
        
        if self.language == "python":
            code = f'''
# Double click element
from selenium.webdriver.common.action_chains import ActionChains

element = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "{selector}"))
)

actions = ActionChains(driver)
actions.double_click(element).perform()
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports() + [
                "from selenium.webdriver.common.action_chains import ActionChains"
            ]
        }
    
    def _generate_selenium_right_click(self, config: Dict[str, Any],
                                     context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium right click action."""
        selector = config.get("selector", "")
        
        if self.language == "python":
            code = f'''
# Right click element
from selenium.webdriver.common.action_chains import ActionChains

element = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "{selector}"))
)

actions = ActionChains(driver)
actions.context_click(element).perform()
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports() + [
                "from selenium.webdriver.common.action_chains import ActionChains"
            ]
        }
    
    def _generate_selenium_screenshot(self, config: Dict[str, Any],
                                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium screenshot action."""
        filename = config.get("filename", "screenshot.png")
        element_selector = config.get("element_selector")
        
        if self.language == "python":
            if element_selector:
                code = f'''
# Take element screenshot
element = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "{element_selector}"))
)
element.screenshot("{filename}")
'''
            else:
                code = f'''
# Take page screenshot
driver.save_screenshot("{filename}")
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports(),
            "file_outputs": [filename]
        }
    
    def _generate_selenium_new_tab(self, config: Dict[str, Any],
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium new tab action."""
        url = config.get("url", "about:blank")
        
        if self.language == "python":
            code = f'''
# Open new tab
driver.execute_script("window.open();")
driver.switch_to.window(driver.window_handles[-1])
driver.get("{url}")

# To switch back to original tab:
# driver.switch_to.window(driver.window_handles[0])
'''
        
        return {
            "code": code,
            "imports": self._get_selenium_imports(),
            "metadata": {
                "action_type": "new_tab", 
                "target_url": url
            }
        }
    
    def _generate_selenium_select(self, config: Dict[str, Any],
                                context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate Selenium dropdown selection."""
        selector = config.get("selector", "")
        value = config.get("value", "")
        by = config.get("by", "value")
        
        if self.language == "python":
            code = f'''
# Select dropdown option
from selenium.webdriver.support.ui import Select

dropdown_element = WebDriverWait(driver, 30).until(
    EC.visibility_of_element_located((By.CSS_SELECTOR, "{selector}"))
)
dropdown = Select(dropdown_element)

'''
            if by == "value":
                code += f'dropdown.select_by_value("{value}")'
            elif by == "label":
                code += f'dropdown.select_by_visible_text("{value}")'
            elif by == "index":
                code += f'dropdown.select_by_index({value})'
        
        return {
            "code": code,
            "imports": self._get_selenium_imports() + [
                "from selenium.webdriver.support.ui import Select"
            ]
        }
    
    # Utility Methods
    
    def _get_playwright_imports(self) -> List[str]:
        """Get standard Playwright imports."""
        if self.language == "python":
            return [
                "from playwright.async_api import async_playwright, expect"
            ]
        elif self.language == "typescript":
            return [
                "import { test, expect } from '@playwright/test';"
            ]
        return []
    
    def _get_selenium_imports(self) -> List[str]:
        """Get standard Selenium imports."""
        if self.language == "python":
            return [
                "from selenium import webdriver",
                "from selenium.webdriver.common.by import By",
                "from selenium.webdriver.support.ui import WebDriverWait",
                "from selenium.webdriver.support import expected_conditions as EC"
            ]
        return []


class AdvancedActionDetector:
    """Detects when advanced actions should be used based on automation data."""
    
    def __init__(self):
        self.detection_patterns = self._load_detection_patterns()
    
    def detect_advanced_actions(self, automation_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect advanced actions in automation data.
        
        Args:
            automation_data: Raw automation data
            
        Returns:
            List of detected advanced actions with configurations
        """
        detected_actions = []
        
        for step_data in automation_data:
            model_output = step_data.get("model_output", {})
            actions = model_output.get("action", [])
            state = step_data.get("state", {})
            
            for action in actions:
                detected = self._detect_single_action(action, state, step_data)
                if detected:
                    detected_actions.extend(detected)
        
        return detected_actions
    
    def _detect_single_action(self, action: Dict[str, Any], state: Dict[str, Any],
                            full_step: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect advanced actions in a single automation step."""
        detected = []
        
        action_type = list(action.keys())[0] if action else ""
        action_data = action.get(action_type, {}) if action else {}
        
        # Detect file upload
        if self._is_file_upload(action_type, action_data, state):
            detected.append(self._create_file_upload_config(action_data, state))
        
        # Detect drag and drop
        elif self._is_drag_drop(action_type, action_data, state):
            detected.append(self._create_drag_drop_config(action_data, state))
        
        # Detect keyboard shortcuts
        elif self._is_keyboard_shortcut(action_type, action_data, state):
            detected.append(self._create_keyboard_config(action_data, state))
        
        # Detect hover actions
        elif self._is_hover_action(action_type, action_data, state):
            detected.append(self._create_hover_config(action_data, state))
        
        return detected
    
    def _is_file_upload(self, action_type: str, action_data: Dict[str, Any], 
                       state: Dict[str, Any]) -> bool:
        """Check if action is a file upload."""
        # Look for file input elements
        interacted_elements = state.get("interacted_element", [])
        for element in interacted_elements:
            attributes = element.get("attributes", {})
            if attributes.get("type") == "file":
                return True
        
        # Look for file paths in action data
        text = action_data.get("text", "")
        if text and ("." in text) and any(ext in text.lower() for ext in [".pdf", ".jpg", ".png", ".doc", ".csv"]):
            return True
        
        return False
    
    def _is_drag_drop(self, action_type: str, action_data: Dict[str, Any],
                     state: Dict[str, Any]) -> bool:
        """Check if action is a drag and drop."""
        # Look for drag-related attributes or patterns
        interacted_elements = state.get("interacted_element", [])
        for element in interacted_elements:
            attributes = element.get("attributes", {})
            if any(attr in attributes for attr in ["draggable", "droppable", "data-drag"]):
                return True
        
        # Look for movement patterns in consecutive actions
        return False
    
    def _is_keyboard_shortcut(self, action_type: str, action_data: Dict[str, Any],
                            state: Dict[str, Any]) -> bool:
        """Check if action is a keyboard shortcut."""
        text = action_data.get("text", "")
        
        # Common keyboard shortcuts
        shortcuts = ["ctrl+", "cmd+", "alt+", "shift+"]
        return any(shortcut in text.lower() for shortcut in shortcuts)
    
    def _is_hover_action(self, action_type: str, action_data: Dict[str, Any],
                       state: Dict[str, Any]) -> bool:
        """Check if action should trigger hover behavior."""
        # Look for hover-specific elements or patterns
        interacted_elements = state.get("interacted_element", [])
        for element in interacted_elements:
            attributes = element.get("attributes", {})
            classes = attributes.get("class", "")
            if any(hover_class in classes.lower() for hover_class in ["dropdown", "menu", "tooltip"]):
                return True
        
        return False
    
    def _create_file_upload_config(self, action_data: Dict[str, Any], 
                                 state: Dict[str, Any]) -> Dict[str, Any]:
        """Create file upload configuration."""
        file_path = action_data.get("text", "")
        interacted_elements = state.get("interacted_element", [])
        
        # Find file input selector
        file_input_selector = ""
        for element in interacted_elements:
            attributes = element.get("attributes", {})
            if attributes.get("type") == "file":
                if attributes.get("id"):
                    file_input_selector = f"#{attributes['id']}"
                elif attributes.get("name"):
                    file_input_selector = f"[name='{attributes['name']}']"
                else:
                    file_input_selector = element.get("css_selector", "")
                break
        
        return {
            "action_type": AdvancedActionType.FILE_UPLOAD.value,
            "config": {
                "file_path": file_path,
                "file_input_selector": file_input_selector,
                "wait_for_upload": True,
                "verify_upload": True
            }
        }
    
    def _create_drag_drop_config(self, action_data: Dict[str, Any],
                               state: Dict[str, Any]) -> Dict[str, Any]:
        """Create drag and drop configuration."""
        # This would need more sophisticated detection logic
        # For now, return a basic configuration
        return {
            "action_type": AdvancedActionType.DRAG_AND_DROP.value,
            "config": {
                "source_selector": "",  # Would be determined from context
                "target_selector": "",  # Would be determined from context
            }
        }
    
    def _create_keyboard_config(self, action_data: Dict[str, Any],
                              state: Dict[str, Any]) -> Dict[str, Any]:
        """Create keyboard shortcut configuration."""
        text = action_data.get("text", "")
        
        # Parse keyboard shortcut
        modifier_keys = []
        keys = []
        
        if "ctrl+" in text.lower():
            modifier_keys.append("Control")
            text = text.lower().replace("ctrl+", "")
        if "cmd+" in text.lower():
            modifier_keys.append("Meta")
            text = text.lower().replace("cmd+", "")
        if "alt+" in text.lower():
            modifier_keys.append("Alt")
            text = text.lower().replace("alt+", "")
        if "shift+" in text.lower():
            modifier_keys.append("Shift")
            text = text.lower().replace("shift+", "")
        
        keys.append(text.strip())
        
        return {
            "action_type": AdvancedActionType.KEYBOARD_SHORTCUT.value,
            "config": {
                "keys": keys,
                "modifier_keys": modifier_keys
            }
        }
    
    def _create_hover_config(self, action_data: Dict[str, Any],
                           state: Dict[str, Any]) -> Dict[str, Any]:
        """Create hover action configuration."""
        interacted_elements = state.get("interacted_element", [])
        selector = ""
        
        if interacted_elements:
            element = interacted_elements[0]
            selector = element.get("css_selector", "")
        
        return {
            "action_type": AdvancedActionType.HOVER.value,
            "config": {
                "selector": selector
            }
        }
    
    def _load_detection_patterns(self) -> Dict[str, Any]:
        """Load patterns for detecting advanced actions."""
        return {
            "file_upload_patterns": [
                {"attribute": "type", "value": "file"},
                {"class_patterns": ["upload", "file-input"]},
                {"text_patterns": [r"\.(pdf|jpg|png|doc|csv|txt)$"]}
            ],
            "drag_drop_patterns": [
                {"attributes": ["draggable", "droppable"]},
                {"class_patterns": ["draggable", "droppable", "sortable"]}
            ],
            "keyboard_patterns": [
                {"text_patterns": [r"ctrl\+", r"cmd\+", r"alt\+", r"shift\+"]}
            ]
        } 