#!/usr/bin/env python3
"""
Page Object Model Generator for Browse-to-Test

This module automatically generates Page Object Model (POM) patterns from browser automation data:
- Analyzes automation flows to identify logical page boundaries
- Extracts common actions and elements into reusable page objects
- Generates maintainable, organized test architecture
- Supports multiple testing frameworks and languages
- Creates hierarchical page structures with inheritance
- Implements best practices for POM design
"""

from typing import Dict, List, Optional, Any, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from pathlib import Path
from collections import defaultdict, Counter


class PageType(Enum):
    """Types of pages that can be detected."""
    LOGIN_PAGE = "login"
    DASHBOARD_PAGE = "dashboard"
    FORM_PAGE = "form"
    LIST_PAGE = "list"
    DETAIL_PAGE = "detail"
    NAVIGATION_PAGE = "navigation"
    MODAL_PAGE = "modal"
    GENERIC_PAGE = "generic"


class ElementType(Enum):
    """Types of elements that can be extracted."""
    BUTTON = "button"
    INPUT = "input"
    LINK = "link"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    TEXT = "text"
    IMAGE = "image"
    CONTAINER = "container"


@dataclass
class PageElement:
    """Represents a page element with its properties."""
    name: str
    element_type: ElementType
    selector: str
    description: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    actions: List[str] = field(default_factory=list)  # click, fill, select, etc.
    validation_rules: List[str] = field(default_factory=list)


@dataclass
class PageAction:
    """Represents an action that can be performed on a page."""
    name: str
    description: str
    elements_used: List[str]  # Element names used in this action
    steps: List[str]  # Step descriptions
    expected_result: Optional[str] = None
    preconditions: List[str] = field(default_factory=list)


@dataclass
class PageObjectDefinition:
    """Complete definition of a page object."""
    name: str
    page_type: PageType
    url_pattern: Optional[str] = None
    description: Optional[str] = None
    elements: List[PageElement] = field(default_factory=list)
    actions: List[PageAction] = field(default_factory=list)
    parent_page: Optional[str] = None  # For inheritance
    child_pages: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    constants: Dict[str, Any] = field(default_factory=dict)


class PageDetector:
    """Detects page boundaries and types from automation data."""
    
    def __init__(self):
        self.page_patterns = self._load_page_patterns()
    
    def detect_pages(self, automation_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect page boundaries and types from automation sequence.
        
        Args:
            automation_data: List of automation steps
            
        Returns:
            List of detected page information
        """
        pages = []
        current_page = None
        page_steps = []
        
        for i, step in enumerate(automation_data):
            # Check if this step indicates a new page
            if self._is_page_transition(step, current_page):
                # Save previous page if it exists
                if current_page and page_steps:
                    page_info = self._analyze_page(current_page, page_steps)
                    pages.append(page_info)
                
                # Start new page
                current_page = self._extract_page_info(step)
                page_steps = [step]
            else:
                page_steps.append(step)
        
        # Handle final page
        if current_page and page_steps:
            page_info = self._analyze_page(current_page, page_steps)
            pages.append(page_info)
        
        return pages
    
    def _is_page_transition(self, step: Dict[str, Any], current_page: Optional[Dict[str, Any]]) -> bool:
        """Check if this step represents a page transition."""
        model_output = step.get("model_output", {})
        actions = model_output.get("action", [])
        
        for action in actions:
            # Navigation actions typically indicate page transitions
            if "go_to_url" in action:
                return True
            
            # URL changes in state might indicate transitions
            if "url" in step.get("state", {}):
                current_url = current_page.get("url", "") if current_page else ""
                new_url = step["state"].get("url", "")
                if new_url and new_url != current_url:
                    return True
            
            # Form submissions often lead to new pages
            if "click_element" in action:
                interacted_elements = step.get("state", {}).get("interacted_element", [])
                for element in interacted_elements:
                    attributes = element.get("attributes", {})
                    if attributes.get("type") == "submit":
                        return True
        
        return False
    
    def _extract_page_info(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Extract basic page information from a step."""
        model_output = step.get("model_output", {})
        actions = model_output.get("action", [])
        state = step.get("state", {})
        
        page_info = {
            "url": None,
            "title": None,
            "elements": [],
            "step_index": 0
        }
        
        # Extract URL
        for action in actions:
            if "go_to_url" in action:
                page_info["url"] = action["go_to_url"].get("url")
                break
        
        # Extract from state if not found in actions
        if not page_info["url"] and "url" in state:
            page_info["url"] = state["url"]
        
        # Extract title if available
        if "title" in state:
            page_info["title"] = state["title"]
        
        return page_info
    
    def _analyze_page(self, page_info: Dict[str, Any], steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze page steps to determine page type and characteristics."""
        url = page_info.get("url", "")
        title = page_info.get("title", "")
        
        # Detect page type based on URL patterns and interactions
        page_type = self._detect_page_type(url, title, steps)
        
        # Extract elements used on this page
        elements = self._extract_page_elements(steps)
        
        # Identify common actions
        actions = self._identify_page_actions(steps, elements)
        
        return {
            "url": url,
            "title": title,
            "page_type": page_type,
            "elements": elements,
            "actions": actions,
            "steps": steps,
            "step_count": len(steps)
        }
    
    def _detect_page_type(self, url: str, title: str, steps: List[Dict[str, Any]]) -> PageType:
        """Detect the type of page based on URL and interactions."""
        url_lower = url.lower() if url else ""
        title_lower = title.lower() if title else ""
        
        # Login page detection
        login_patterns = ["login", "signin", "auth", "authenticate"]
        if any(pattern in url_lower or pattern in title_lower for pattern in login_patterns):
            return PageType.LOGIN_PAGE
        
        # Dashboard detection
        dashboard_patterns = ["dashboard", "home", "main", "overview"]
        if any(pattern in url_lower or pattern in title_lower for pattern in dashboard_patterns):
            return PageType.DASHBOARD_PAGE
        
        # Form page detection
        form_patterns = ["form", "create", "edit", "add", "submit"]
        if any(pattern in url_lower or pattern in title_lower for pattern in form_patterns):
            return PageType.FORM_PAGE
        
        # List page detection
        list_patterns = ["list", "table", "index", "browse"]
        if any(pattern in url_lower or pattern in title_lower for pattern in list_patterns):
            return PageType.LIST_PAGE
        
        # Detail page detection
        detail_patterns = ["detail", "view", "show", "/\\d+", "profile"]
        if any(pattern in url_lower or pattern in title_lower for pattern in detail_patterns):
            return PageType.DETAIL_PAGE
        
        # Check interaction patterns
        has_form_inputs = self._has_form_inputs(steps)
        has_navigation = self._has_navigation_elements(steps)
        
        if has_form_inputs:
            return PageType.FORM_PAGE
        elif has_navigation:
            return PageType.NAVIGATION_PAGE
        
        return PageType.GENERIC_PAGE
    
    def _has_form_inputs(self, steps: List[Dict[str, Any]]) -> bool:
        """Check if page has form input interactions."""
        for step in steps:
            model_output = step.get("model_output", {})
            actions = model_output.get("action", [])
            
            for action in actions:
                if "input_text" in action or "fill" in action:
                    return True
        
        return False
    
    def _has_navigation_elements(self, steps: List[Dict[str, Any]]) -> bool:
        """Check if page has navigation elements."""
        nav_patterns = ["nav", "menu", "header", "sidebar"]
        
        for step in steps:
            interacted_elements = step.get("state", {}).get("interacted_element", [])
            for element in interacted_elements:
                attributes = element.get("attributes", {})
                classes = attributes.get("class", "").lower()
                
                if any(pattern in classes for pattern in nav_patterns):
                    return True
        
        return False
    
    def _extract_page_elements(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract unique elements used on this page."""
        elements = {}
        
        for step in steps:
            interacted_elements = step.get("state", {}).get("interacted_element", [])
            
            for element in interacted_elements:
                # Create unique identifier for element
                element_id = self._create_element_id(element)
                
                if element_id not in elements:
                    elements[element_id] = {
                        "id": element_id,
                        "selector": element.get("css_selector", ""),
                        "xpath": element.get("xpath", ""),
                        "attributes": element.get("attributes", {}),
                        "type": self._detect_element_type(element),
                        "actions": set(),
                        "text_content": element.get("text_content", "")
                    }
                
                # Add action for this element
                action_type = self._get_action_type_for_element(step, element)
                if action_type:
                    elements[element_id]["actions"].add(action_type)
        
        # Convert sets to lists for JSON serialization
        for element in elements.values():
            element["actions"] = list(element["actions"])
        
        return list(elements.values())
    
    def _create_element_id(self, element: Dict[str, Any]) -> str:
        """Create a unique identifier for an element."""
        attributes = element.get("attributes", {})
        
        # Prefer stable identifiers
        if attributes.get("id"):
            return f"id_{attributes['id']}"
        elif attributes.get("data-testid"):
            return f"testid_{attributes['data-testid']}"
        elif attributes.get("name"):
            return f"name_{attributes['name']}"
        else:
            # Use CSS selector as fallback
            css_selector = element.get("css_selector", "")
            # Clean up selector for use as identifier
            clean_selector = re.sub(r'[^a-zA-Z0-9_]', '_', css_selector)
            return f"css_{clean_selector}"[:50]  # Limit length
    
    def _detect_element_type(self, element: Dict[str, Any]) -> ElementType:
        """Detect the type of an element."""
        attributes = element.get("attributes", {})
        tag_name = attributes.get("tagName", "").lower()
        element_type = attributes.get("type", "").lower()
        
        if tag_name == "button" or element_type == "button":
            return ElementType.BUTTON
        elif tag_name == "input":
            if element_type in ["text", "email", "password", "number"]:
                return ElementType.INPUT
            elif element_type == "checkbox":
                return ElementType.CHECKBOX
            elif element_type == "radio":
                return ElementType.RADIO
        elif tag_name == "select":
            return ElementType.DROPDOWN
        elif tag_name == "a":
            return ElementType.LINK
        elif tag_name == "img":
            return ElementType.IMAGE
        elif tag_name in ["div", "span", "section"]:
            return ElementType.CONTAINER
        elif element.get("text_content"):
            return ElementType.TEXT
        
        return ElementType.CONTAINER
    
    def _get_action_type_for_element(self, step: Dict[str, Any], element: Dict[str, Any]) -> Optional[str]:
        """Get the action type performed on an element in this step."""
        model_output = step.get("model_output", {})
        actions = model_output.get("action", [])
        
        for action in actions:
            if "click" in action or "click_element" in action:
                return "click"
            elif "input_text" in action or "fill" in action:
                return "fill"
            elif "select_option" in action:
                return "select"
        
        return None
    
    def _identify_page_actions(self, steps: List[Dict[str, Any]], elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify common actions that can be performed on this page."""
        actions = []
        
        # Group steps by action patterns
        action_groups = self._group_actions_by_pattern(steps)
        
        for pattern, step_group in action_groups.items():
            action_name = self._generate_action_name(pattern, step_group)
            action_description = self._generate_action_description(step_group)
            elements_used = self._get_elements_used_in_steps(step_group)
            
            actions.append({
                "name": action_name,
                "description": action_description,
                "elements_used": elements_used,
                "steps": [self._describe_step(step) for step in step_group]
            })
        
        return actions
    
    def _group_actions_by_pattern(self, steps: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group steps by common action patterns."""
        # Simple grouping - could be more sophisticated
        return {"default": steps}
    
    def _generate_action_name(self, pattern: str, steps: List[Dict[str, Any]]) -> str:
        """Generate a descriptive name for an action."""
        if len(steps) == 1:
            return self._describe_step(steps[0])
        else:
            return f"perform_{pattern}_workflow"
    
    def _generate_action_description(self, steps: List[Dict[str, Any]]) -> str:
        """Generate a description for a group of steps."""
        if len(steps) == 1:
            return f"Performs {self._describe_step(steps[0])}"
        else:
            return f"Performs a workflow with {len(steps)} steps"
    
    def _get_elements_used_in_steps(self, steps: List[Dict[str, Any]]) -> List[str]:
        """Get list of element IDs used in the given steps."""
        element_ids = set()
        
        for step in steps:
            interacted_elements = step.get("state", {}).get("interacted_element", [])
            for element in interacted_elements:
                element_id = self._create_element_id(element)
                element_ids.add(element_id)
        
        return list(element_ids)
    
    def _describe_step(self, step: Dict[str, Any]) -> str:
        """Generate a description for a single step."""
        model_output = step.get("model_output", {})
        actions = model_output.get("action", [])
        
        if not actions:
            return "unknown_action"
        
        action = actions[0]
        action_type = list(action.keys())[0]
        
        if action_type == "go_to_url":
            return "navigate_to_page"
        elif action_type in ["click", "click_element"]:
            return "click_element"
        elif action_type in ["input_text", "fill"]:
            return "fill_input"
        elif action_type == "select_option":
            return "select_option"
        else:
            return action_type.replace("_", " ")
    
    def _load_page_patterns(self) -> Dict[str, Any]:
        """Load patterns for page detection."""
        return {
            "login_patterns": ["login", "signin", "auth", "authenticate"],
            "dashboard_patterns": ["dashboard", "home", "main", "overview"],
            "form_patterns": ["form", "create", "edit", "add", "submit"],
            "list_patterns": ["list", "table", "index", "browse"],
            "detail_patterns": ["detail", "view", "show", "profile"]
        }


class ElementAnalyzer:
    """Analyzes elements to determine optimal naming and organization."""
    
    def analyze_elements(self, elements: List[Dict[str, Any]]) -> List[PageElement]:
        """Analyze raw elements and create PageElement objects."""
        page_elements = []
        
        for element in elements:
            # Generate meaningful name
            name = self._generate_element_name(element)
            
            # Determine element type
            element_type = ElementType(element.get("type", "container"))
            
            # Choose best selector
            selector = self._choose_best_selector(element)
            
            # Generate description
            description = self._generate_element_description(element)
            
            page_element = PageElement(
                name=name,
                element_type=element_type,
                selector=selector,
                description=description,
                attributes=element.get("attributes", {}),
                actions=element.get("actions", [])
            )
            
            page_elements.append(page_element)
        
        return page_elements
    
    def _generate_element_name(self, element: Dict[str, Any]) -> str:
        """Generate a meaningful name for an element."""
        attributes = element.get("attributes", {})
        text_content = element.get("text_content", "").strip()
        
        # Try to use semantic attributes
        if attributes.get("data-testid"):
            return self._clean_name(attributes["data-testid"])
        
        if attributes.get("id"):
            return self._clean_name(attributes["id"])
        
        if attributes.get("name"):
            return self._clean_name(attributes["name"])
        
        # Use text content for buttons/links
        if text_content and element.get("type") in ["button", "link"]:
            return self._clean_name(text_content)
        
        # Use placeholder for inputs
        if attributes.get("placeholder"):
            return self._clean_name(attributes["placeholder"]) + "_input"
        
        # Use type and attributes as fallback
        element_type = element.get("type", "element")
        if attributes.get("class"):
            classes = attributes["class"].split()
            meaningful_class = self._find_meaningful_class(classes)
            if meaningful_class:
                return f"{meaningful_class}_{element_type}"
        
        return f"unnamed_{element_type}"
    
    def _clean_name(self, name: str) -> str:
        """Clean a name to make it a valid identifier."""
        # Convert to lowercase and replace non-alphanumeric with underscore
        clean = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        # Remove multiple underscores
        clean = re.sub(r'_+', '_', clean)
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        # Ensure it starts with a letter
        if clean and clean[0].isdigit():
            clean = f"element_{clean}"
        
        return clean or "unnamed_element"
    
    def _find_meaningful_class(self, classes: List[str]) -> Optional[str]:
        """Find the most meaningful class name."""
        # Avoid utility classes
        utility_patterns = [
            r'^[a-f0-9]{6,}$',  # Hex colors
            r'^[mpt][xy]?-\d+$',  # Margin/padding utilities
            r'^text-',  # Text utilities
            r'^bg-',   # Background utilities
            r'^flex',  # Flex utilities
        ]
        
        for class_name in classes:
            # Skip utility classes
            if any(re.match(pattern, class_name) for pattern in utility_patterns):
                continue
            
            # Prefer semantic class names
            if len(class_name) > 3 and class_name.isalpha():
                return class_name
        
        return None
    
    def _choose_best_selector(self, element: Dict[str, Any]) -> str:
        """Choose the best selector for an element."""
        attributes = element.get("attributes", {})
        
        # Preference order for selectors
        if attributes.get("data-testid"):
            return f'[data-testid="{attributes["data-testid"]}"]'
        
        if attributes.get("id"):
            return f'#{attributes["id"]}'
        
        if attributes.get("name"):
            return f'[name="{attributes["name"]}"]'
        
        # Use CSS selector as fallback
        css_selector = element.get("css_selector", "")
        if css_selector:
            return css_selector
        
        # Use XPath as last resort
        xpath = element.get("xpath", "")
        if xpath:
            return xpath
        
        return "[data-testid='unknown']"
    
    def _generate_element_description(self, element: Dict[str, Any]) -> str:
        """Generate a description for an element."""
        element_type = element.get("type", "element")
        text_content = element.get("text_content", "").strip()
        attributes = element.get("attributes", {})
        
        if text_content:
            return f"{element_type.title()} with text '{text_content[:50]}'"
        elif attributes.get("placeholder"):
            return f"{element_type.title()} with placeholder '{attributes['placeholder']}'"
        elif attributes.get("aria-label"):
            return f"{element_type.title()} with aria-label '{attributes['aria-label']}'"
        else:
            return f"{element_type.title()} element"


class PageObjectCodeGenerator:
    """Generates page object code in various languages and frameworks."""
    
    def __init__(self, framework: str = "playwright", language: str = "python"):
        self.framework = framework
        self.language = language
    
    def generate_page_object(self, page_def: PageObjectDefinition) -> str:
        """Generate page object code from definition."""
        if self.language == "python":
            return self._generate_python_page_object(page_def)
        elif self.language == "typescript":
            return self._generate_typescript_page_object(page_def)
        elif self.language == "javascript":
            return self._generate_javascript_page_object(page_def)
        else:
            raise ValueError(f"Unsupported language: {self.language}")
    
    def _generate_python_page_object(self, page_def: PageObjectDefinition) -> str:
        """Generate Python page object code."""
        class_name = self._to_class_name(page_def.name)
        
        # Generate imports
        imports = self._generate_python_imports(page_def)
        
        # Generate class definition
        parent_class = "BasePage" if page_def.parent_page else "object"
        class_def = f"class {class_name}({parent_class}):"
        
        # Generate class docstring
        docstring = self._generate_python_docstring(page_def)
        
        # Generate constructor
        constructor = self._generate_python_constructor(page_def)
        
        # Generate element properties
        elements = self._generate_python_elements(page_def.elements)
        
        # Generate action methods
        actions = self._generate_python_actions(page_def.actions)
        
        # Combine all parts
        code_parts = [
            imports,
            "",
            class_def,
            docstring,
            "",
            constructor,
            "",
            elements,
            "",
            actions
        ]
        
        return "\n".join(code_parts)
    
    def _generate_python_imports(self, page_def: PageObjectDefinition) -> str:
        """Generate Python imports for page object."""
        imports = []
        
        if self.framework == "playwright":
            imports.extend([
                "from playwright.sync_api import Page, Locator",
                "from typing import Optional"
            ])
        elif self.framework == "selenium":
            imports.extend([
                "from selenium.webdriver.remote.webdriver import WebDriver",
                "from selenium.webdriver.common.by import By",
                "from selenium.webdriver.support.ui import WebDriverWait",
                "from selenium.webdriver.support import expected_conditions as EC",
                "from typing import Optional"
            ])
        
        # Add custom imports
        imports.extend(page_def.imports)
        
        return "\n".join(imports)
    
    def _generate_python_docstring(self, page_def: PageObjectDefinition) -> str:
        """Generate Python class docstring."""
        lines = ['    """']
        
        if page_def.description:
            lines.append(f"    {page_def.description}")
        else:
            lines.append(f"    Page object for {page_def.name}")
        
        if page_def.url_pattern:
            lines.append(f"    URL Pattern: {page_def.url_pattern}")
        
        lines.append('    """')
        
        return "\n".join(lines)
    
    def _generate_python_constructor(self, page_def: PageObjectDefinition) -> str:
        """Generate Python constructor."""
        if self.framework == "playwright":
            return '''    def __init__(self, page: Page):
        """Initialize the page object with a Playwright page instance."""
        self.page = page'''
        elif self.framework == "selenium":
            return '''    def __init__(self, driver: WebDriver):
        """Initialize the page object with a Selenium WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)'''
        else:
            return '''    def __init__(self, page):
        """Initialize the page object."""
        self.page = page'''
    
    def _generate_python_elements(self, elements: List[PageElement]) -> str:
        """Generate Python element properties."""
        if not elements:
            return "    # No elements defined"
        
        lines = ["    # Page Elements"]
        
        for element in elements:
            property_name = element.name
            selector = element.selector
            description = element.description or f"{element.element_type.value} element"
            
            if self.framework == "playwright":
                lines.extend([
                    f"    @property",
                    f"    def {property_name}(self) -> Locator:",
                    f'        """{description}"""',
                    f'        return self.page.locator("{selector}")',
                    ""
                ])
            elif self.framework == "selenium":
                lines.extend([
                    f"    @property", 
                    f"    def {property_name}(self):",
                    f'        """{description}"""',
                    f'        return self.driver.find_element(By.CSS_SELECTOR, "{selector}")',
                    ""
                ])
        
        return "\n".join(lines)
    
    def _generate_python_actions(self, actions: List[PageAction]) -> str:
        """Generate Python action methods."""
        if not actions:
            return "    # No actions defined"
        
        lines = ["    # Page Actions"]
        
        for action in actions:
            method_name = self._to_method_name(action.name)
            description = action.description
            
            lines.extend([
                f"    def {method_name}(self):",
                f'        """{description}"""',
                f"        # TODO: Implement {action.name}",
                f"        pass",
                ""
            ])
        
        return "\n".join(lines)
    
    def _generate_typescript_page_object(self, page_def: PageObjectDefinition) -> str:
        """Generate TypeScript page object code."""
        class_name = self._to_class_name(page_def.name)
        
        # Generate imports
        imports = self._generate_typescript_imports(page_def)
        
        # Generate class definition
        parent_class = page_def.parent_page or "BasePage"
        class_def = f"export class {class_name} extends {parent_class} {{"
        
        # Generate constructor
        constructor = self._generate_typescript_constructor(page_def)
        
        # Generate element getters
        elements = self._generate_typescript_elements(page_def.elements)
        
        # Generate action methods
        actions = self._generate_typescript_actions(page_def.actions)
        
        # Combine all parts
        code_parts = [
            imports,
            "",
            f"/**",
            f" * {page_def.description or f'Page object for {page_def.name}'}",
            f" */",
            class_def,
            constructor,
            "",
            elements,
            "",
            actions,
            "}"
        ]
        
        return "\n".join(code_parts)
    
    def _generate_typescript_imports(self, page_def: PageObjectDefinition) -> str:
        """Generate TypeScript imports."""
        imports = []
        
        if self.framework == "playwright":
            imports.append("import { Page, Locator } from '@playwright/test';")
        
        # Add custom imports
        imports.extend(page_def.imports)
        
        return "\n".join(imports)
    
    def _generate_typescript_constructor(self, page_def: PageObjectDefinition) -> str:
        """Generate TypeScript constructor."""
        if self.framework == "playwright":
            return '''    constructor(private page: Page) {
        super(page);
    }'''
        else:
            return '''    constructor(page: any) {
        super(page);
    }'''
    
    def _generate_typescript_elements(self, elements: List[PageElement]) -> str:
        """Generate TypeScript element getters."""
        if not elements:
            return "    // No elements defined"
        
        lines = ["    // Page Elements"]
        
        for element in elements:
            property_name = element.name
            selector = element.selector
            description = element.description or f"{element.element_type.value} element"
            
            if self.framework == "playwright":
                lines.extend([
                    f"    /**",
                    f"     * {description}",
                    f"     */",
                    f"    get {property_name}(): Locator {{",
                    f'        return this.page.locator("{selector}");',
                    f"    }}",
                    ""
                ])
        
        return "\n".join(lines)
    
    def _generate_typescript_actions(self, actions: List[PageAction]) -> str:
        """Generate TypeScript action methods."""
        if not actions:
            return "    // No actions defined"
        
        lines = ["    // Page Actions"]
        
        for action in actions:
            method_name = self._to_method_name(action.name)
            description = action.description
            
            lines.extend([
                f"    /**",
                f"     * {description}",
                f"     */",
                f"    async {method_name}(): Promise<void> {{",
                f"        // TODO: Implement {action.name}",
                f"    }}",
                ""
            ])
        
        return "\n".join(lines)
    
    def _generate_javascript_page_object(self, page_def: PageObjectDefinition) -> str:
        """Generate JavaScript page object code."""
        # Similar to TypeScript but without type annotations
        class_name = self._to_class_name(page_def.name)
        
        code_parts = [
            "/**",
            f" * {page_def.description or f'Page object for {page_def.name}'}",
            " */",
            f"class {class_name} {{",
            "",
            "    constructor(page) {",
            "        this.page = page;",
            "    }",
            "",
            self._generate_javascript_elements(page_def.elements),
            "",
            self._generate_javascript_actions(page_def.actions),
            "}",
            "",
            f"module.exports = {class_name};"
        ]
        
        return "\n".join(code_parts)
    
    def _generate_javascript_elements(self, elements: List[PageElement]) -> str:
        """Generate JavaScript element getters."""
        if not elements:
            return "    // No elements defined"
        
        lines = ["    // Page Elements"]
        
        for element in elements:
            property_name = element.name
            selector = element.selector
            description = element.description or f"{element.element_type.value} element"
            
            lines.extend([
                f"    /**",
                f"     * {description}",
                f"     */",
                f"    get {property_name}() {{",
                f'        return this.page.locator("{selector}");',
                f"    }}",
                ""
            ])
        
        return "\n".join(lines)
    
    def _generate_javascript_actions(self, actions: List[PageAction]) -> str:
        """Generate JavaScript action methods."""
        if not actions:
            return "    // No actions defined"
        
        lines = ["    // Page Actions"]
        
        for action in actions:
            method_name = self._to_method_name(action.name)
            description = action.description
            
            lines.extend([
                f"    /**",
                f"     * {description}",
                f"     */",
                f"    async {method_name}() {{",
                f"        // TODO: Implement {action.name}",
                f"    }}",
                ""
            ])
        
        return "\n".join(lines)
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        words = re.findall(r'\w+', name)
        return ''.join(word.capitalize() for word in words) + "Page"
    
    def _to_method_name(self, name: str) -> str:
        """Convert name to camelCase method name."""
        words = re.findall(r'\w+', name)
        if not words:
            return "unknownAction"
        
        return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


class PageObjectModelGenerator:
    """Main class for generating complete Page Object Model architecture."""
    
    def __init__(self, framework: str = "playwright", language: str = "python"):
        self.framework = framework
        self.language = language
        self.page_detector = PageDetector()
        self.element_analyzer = ElementAnalyzer()
        self.code_generator = PageObjectCodeGenerator(framework, language)
    
    def generate_page_objects(self, automation_data: List[Dict[str, Any]], 
                            output_dir: str = "page_objects") -> Dict[str, str]:
        """
        Generate complete page object model from automation data.
        
        Args:
            automation_data: Browser automation sequence data
            output_dir: Directory to save generated page objects
            
        Returns:
            Dictionary of filename -> code content
        """
        # Detect pages from automation data
        detected_pages = self.page_detector.detect_pages(automation_data)
        
        # Create page object definitions
        page_definitions = []
        for page_data in detected_pages:
            page_def = self._create_page_definition(page_data)
            page_definitions.append(page_def)
        
        # Organize pages into hierarchy
        organized_pages = self._organize_page_hierarchy(page_definitions)
        
        # Generate code for each page
        generated_files = {}
        
        # Generate base page first
        base_page_code = self._generate_base_page()
        base_filename = f"base_page.{self._get_file_extension()}"
        generated_files[base_filename] = base_page_code
        
        # Generate individual page objects
        for page_def in organized_pages:
            page_code = self.code_generator.generate_page_object(page_def)
            filename = f"{self._to_filename(page_def.name)}.{self._get_file_extension()}"
            generated_files[filename] = page_code
        
        # Generate index/module file
        index_code = self._generate_index_file(organized_pages)
        index_filename = f"__init__.{self._get_file_extension()}"
        generated_files[index_filename] = index_code
        
        return generated_files
    
    def _create_page_definition(self, page_data: Dict[str, Any]) -> PageObjectDefinition:
        """Create a PageObjectDefinition from detected page data."""
        # Analyze elements
        elements = self.element_analyzer.analyze_elements(page_data.get("elements", []))
        
        # Create actions from page data
        actions = []
        for action_data in page_data.get("actions", []):
            action = PageAction(
                name=action_data["name"],
                description=action_data["description"],
                elements_used=action_data.get("elements_used", []),
                steps=action_data.get("steps", [])
            )
            actions.append(action)
        
        # Determine page name
        page_name = self._generate_page_name(page_data)
        
        # Create page definition
        page_def = PageObjectDefinition(
            name=page_name,
            page_type=PageType(page_data.get("page_type", "generic")),
            url_pattern=page_data.get("url"),
            description=f"Page object for {page_name}",
            elements=elements,
            actions=actions
        )
        
        return page_def
    
    def _generate_page_name(self, page_data: Dict[str, Any]) -> str:
        """Generate a meaningful page name from page data."""
        url = page_data.get("url", "")
        title = page_data.get("title", "")
        page_type = page_data.get("page_type", "")
        
        # Try to extract name from URL
        if url:
            # Remove protocol and domain
            path = re.sub(r'^https?://[^/]+', '', url)
            # Extract meaningful parts
            path_parts = [part for part in path.split('/') if part and not part.isdigit()]
            if path_parts:
                return '_'.join(path_parts)
        
        # Use title if available
        if title:
            clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', title)
            return clean_title.lower().replace(' ', '_')
        
        # Use page type as fallback
        return page_type + "_page"
    
    def _organize_page_hierarchy(self, page_definitions: List[PageObjectDefinition]) -> List[PageObjectDefinition]:
        """Organize pages into a logical hierarchy."""
        # Simple organization for now - could be more sophisticated
        # Group by page type and establish inheritance
        
        organized = []
        
        # Create base pages for each type
        page_types = set(page_def.page_type for page_def in page_definitions)
        
        for page_def in page_definitions:
            # Set parent based on page type patterns
            if page_def.page_type == PageType.LOGIN_PAGE:
                page_def.parent_page = "FormBasePage"
            elif page_def.page_type == PageType.FORM_PAGE:
                page_def.parent_page = "FormBasePage"
            elif page_def.page_type == PageType.LIST_PAGE:
                page_def.parent_page = "ListBasePage"
            else:
                page_def.parent_page = "BasePage"
            
            organized.append(page_def)
        
        return organized
    
    def _generate_base_page(self) -> str:
        """Generate base page class code."""
        if self.language == "python":
            return self._generate_python_base_page()
        elif self.language == "typescript":
            return self._generate_typescript_base_page()
        elif self.language == "javascript":
            return self._generate_javascript_base_page()
        else:
            return ""
    
    def _generate_python_base_page(self) -> str:
        """Generate Python base page class."""
        if self.framework == "playwright":
            return '''"""Base page class for all page objects."""

from playwright.sync_api import Page, Locator
from typing import Optional


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, page: Page):
        """Initialize the base page with a Playwright page instance."""
        self.page = page
    
    def wait_for_page_load(self, timeout: int = 30000) -> None:
        """Wait for the page to fully load."""
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)
    
    def get_title(self) -> str:
        """Get the page title."""
        return self.page.title()
    
    def get_url(self) -> str:
        """Get the current page URL."""
        return self.page.url
    
    def is_element_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        return self.page.locator(selector).is_visible()
    
    def wait_for_element(self, selector: str, timeout: int = 30000) -> Locator:
        """Wait for an element to be visible."""
        locator = self.page.locator(selector)
        locator.wait_for(state="visible", timeout=timeout)
        return locator


class FormBasePage(BasePage):
    """Base class for form pages."""
    
    def fill_and_submit_form(self, form_data: dict) -> None:
        """Fill form fields and submit."""
        # Override in subclasses
        pass


class ListBasePage(BasePage):
    """Base class for list/table pages."""
    
    def get_row_count(self) -> int:
        """Get the number of rows in the list."""
        # Override in subclasses
        return 0
'''
        
        elif self.framework == "selenium":
            return '''"""Base page class for all page objects."""

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional


class BasePage:
    """Base class for all page objects."""
    
    def __init__(self, driver: WebDriver):
        """Initialize the base page with a WebDriver instance."""
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
    
    def wait_for_page_load(self, timeout: int = 30) -> None:
        """Wait for the page to fully load."""
        self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
    
    def get_title(self) -> str:
        """Get the page title."""
        return self.driver.title
    
    def get_url(self) -> str:
        """Get the current page URL."""
        return self.driver.current_url
    
    def is_element_visible(self, selector: str) -> bool:
        """Check if an element is visible."""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.is_displayed()
        except:
            return False
    
    def wait_for_element(self, selector: str, timeout: int = 30):
        """Wait for an element to be visible."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))


class FormBasePage(BasePage):
    """Base class for form pages."""
    
    def fill_and_submit_form(self, form_data: dict) -> None:
        """Fill form fields and submit."""
        # Override in subclasses
        pass


class ListBasePage(BasePage):
    """Base class for list/table pages."""
    
    def get_row_count(self) -> int:
        """Get the number of rows in the list."""
        # Override in subclasses
        return 0
'''
    
    def _generate_typescript_base_page(self) -> str:
        """Generate TypeScript base page class."""
        return '''/**
 * Base page class for all page objects.
 */

import { Page, Locator } from '@playwright/test';

export class BasePage {
    constructor(protected page: Page) {}

    /**
     * Wait for the page to fully load.
     */
    async waitForPageLoad(timeout: number = 30000): Promise<void> {
        await this.page.waitForLoadState('domcontentloaded', { timeout });
    }

    /**
     * Get the page title.
     */
    async getTitle(): Promise<string> {
        return await this.page.title();
    }

    /**
     * Get the current page URL.
     */
    getUrl(): string {
        return this.page.url();
    }

    /**
     * Check if an element is visible.
     */
    async isElementVisible(selector: string): Promise<boolean> {
        return await this.page.locator(selector).isVisible();
    }

    /**
     * Wait for an element to be visible.
     */
    async waitForElement(selector: string, timeout: number = 30000): Promise<Locator> {
        const locator = this.page.locator(selector);
        await locator.waitFor({ state: 'visible', timeout });
        return locator;
    }
}

/**
 * Base class for form pages.
 */
export class FormBasePage extends BasePage {
    /**
     * Fill form fields and submit.
     */
    async fillAndSubmitForm(formData: Record<string, string>): Promise<void> {
        // Override in subclasses
    }
}

/**
 * Base class for list/table pages.
 */
export class ListBasePage extends BasePage {
    /**
     * Get the number of rows in the list.
     */
    async getRowCount(): Promise<number> {
        // Override in subclasses
        return 0;
    }
}
'''
    
    def _generate_javascript_base_page(self) -> str:
        """Generate JavaScript base page class."""
        return '''/**
 * Base page class for all page objects.
 */

class BasePage {
    constructor(page) {
        this.page = page;
    }

    /**
     * Wait for the page to fully load.
     */
    async waitForPageLoad(timeout = 30000) {
        await this.page.waitForLoadState('domcontentloaded', { timeout });
    }

    /**
     * Get the page title.
     */
    async getTitle() {
        return await this.page.title();
    }

    /**
     * Get the current page URL.
     */
    getUrl() {
        return this.page.url();
    }

    /**
     * Check if an element is visible.
     */
    async isElementVisible(selector) {
        return await this.page.locator(selector).isVisible();
    }

    /**
     * Wait for an element to be visible.
     */
    async waitForElement(selector, timeout = 30000) {
        const locator = this.page.locator(selector);
        await locator.waitFor({ state: 'visible', timeout });
        return locator;
    }
}

/**
 * Base class for form pages.
 */
class FormBasePage extends BasePage {
    /**
     * Fill form fields and submit.
     */
    async fillAndSubmitForm(formData) {
        // Override in subclasses
    }
}

/**
 * Base class for list/table pages.
 */
class ListBasePage extends BasePage {
    /**
     * Get the number of rows in the list.
     */
    async getRowCount() {
        // Override in subclasses
        return 0;
    }
}

module.exports = { BasePage, FormBasePage, ListBasePage };
'''
    
    def _generate_index_file(self, page_definitions: List[PageObjectDefinition]) -> str:
        """Generate index/module file that exports all page objects."""
        if self.language == "python":
            return self._generate_python_index(page_definitions)
        elif self.language in ["typescript", "javascript"]:
            return self._generate_typescript_index(page_definitions)
        else:
            return ""
    
    def _generate_python_index(self, page_definitions: List[PageObjectDefinition]) -> str:
        """Generate Python __init__.py file."""
        imports = ["from .base_page import BasePage, FormBasePage, ListBasePage"]
        
        for page_def in page_definitions:
            class_name = self._to_class_name(page_def.name)
            module_name = self._to_filename(page_def.name)
            imports.append(f"from .{module_name} import {class_name}")
        
        exports = ["__all__ = ["]
        exports.append('    "BasePage",')
        exports.append('    "FormBasePage",')
        exports.append('    "ListBasePage",')
        
        for page_def in page_definitions:
            class_name = self._to_class_name(page_def.name)
            exports.append(f'    "{class_name}",')
        
        exports.append("]")
        
        return "\n".join(imports) + "\n\n" + "\n".join(exports)
    
    def _generate_typescript_index(self, page_definitions: List[PageObjectDefinition]) -> str:
        """Generate TypeScript index file."""
        exports = ["export { BasePage, FormBasePage, ListBasePage } from './base_page';"]
        
        for page_def in page_definitions:
            class_name = self._to_class_name(page_def.name)
            module_name = self._to_filename(page_def.name)
            exports.append(f"export {{ {class_name} }} from './{module_name}';")
        
        return "\n".join(exports)
    
    def _get_file_extension(self) -> str:
        """Get file extension for the current language."""
        extensions = {
            "python": "py",
            "typescript": "ts", 
            "javascript": "js"
        }
        return extensions.get(self.language, "txt")
    
    def _to_filename(self, name: str) -> str:
        """Convert name to filename format."""
        # Convert to snake_case
        name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower())
        name = re.sub(r'_+', '_', name)
        return name.strip('_')
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        words = re.findall(r'\w+', name)
        return ''.join(word.capitalize() for word in words) + "Page" 