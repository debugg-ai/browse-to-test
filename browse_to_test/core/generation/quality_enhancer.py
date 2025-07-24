#!/usr/bin/env python3
"""
Enhanced Test Quality System for Browse-to-Test

This module provides advanced features for generating high-quality, robust test scripts:
- Smart selector generation with fallback strategies
- Robust waiting mechanisms with retry logic
- Enhanced assertion generation
- Code quality analysis and recommendations
- Best practices enforcement
"""

from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import re
import json
from pathlib import Path


class SelectorStrategy(Enum):
    """Selector generation strategies."""
    DATA_TESTID = "data-testid"  # Preferred - semantic test identifiers
    ARIA_LABEL = "aria-label"   # Accessible - ARIA labels
    SEMANTIC = "semantic"       # Semantic HTML elements (button, input, etc.)
    CSS_CLASS = "css-class"     # CSS classes (less stable)
    XPATH = "xpath"            # XPath (most flexible but brittle)
    TEXT_CONTENT = "text"      # Text content matching


class WaitStrategy(Enum):
    """Waiting strategy types."""
    ELEMENT_VISIBLE = "visible"
    ELEMENT_ATTACHED = "attached"
    ELEMENT_STABLE = "stable"
    NETWORK_IDLE = "networkidle"
    LOAD_STATE = "load"
    CUSTOM_CONDITION = "custom"


@dataclass
class SelectorConfig:
    """Configuration for selector generation."""
    preferred_strategies: List[SelectorStrategy] = field(default_factory=lambda: [
        SelectorStrategy.DATA_TESTID,
        SelectorStrategy.ARIA_LABEL,
        SelectorStrategy.SEMANTIC,
        SelectorStrategy.CSS_CLASS,
        SelectorStrategy.XPATH
    ])
    fallback_enabled: bool = True
    stability_score_threshold: float = 0.7
    generate_multiple_selectors: bool = True
    include_selector_comments: bool = True


@dataclass
class WaitConfig:
    """Configuration for wait mechanisms."""
    default_timeout: int = 30000
    retry_attempts: int = 3
    retry_delay: int = 1000
    network_idle_timeout: int = 500
    stability_check_duration: int = 100
    custom_wait_conditions: Dict[str, str] = field(default_factory=dict)


@dataclass
class AssertionConfig:
    """Configuration for assertion generation."""
    auto_generate_assertions: bool = True
    assertion_types: List[str] = field(default_factory=lambda: [
        "visibility", "text_content", "attribute_value", "element_count"
    ])
    soft_assertions: bool = True
    assertion_messages: bool = True
    screenshot_on_failure: bool = True


@dataclass
class QualityMetrics:
    """Quality metrics for generated test scripts."""
    selector_stability_score: float = 0.0
    wait_robustness_score: float = 0.0
    assertion_coverage_score: float = 0.0
    maintainability_score: float = 0.0
    overall_quality_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)


class SmartSelectorGenerator:
    """Generates smart, stable selectors with fallback strategies."""
    
    def __init__(self, config: SelectorConfig):
        self.config = config
    
    def generate_selector(self, element_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate multiple selector strategies for an element.
        
        Args:
            element_data: Element information from automation data
            
        Returns:
            Dict containing primary selector, fallbacks, and stability info
        """
        selectors = {}
        stability_scores = {}
        
        # Extract element attributes
        attributes = element_data.get("attributes", {})
        xpath = element_data.get("xpath", "")
        css_selector = element_data.get("css_selector", "")
        text_content = element_data.get("text_content", "")
        
        # Strategy 1: data-testid (most stable)
        if attributes.get("data-testid"):
            selectors["data_testid"] = f"[data-testid='{attributes['data-testid']}']"
            stability_scores["data_testid"] = 0.95
        
        # Strategy 2: ARIA labels (accessible and stable)
        if attributes.get("aria-label"):
            selectors["aria_label"] = f"[aria-label='{attributes['aria-label']}']"
            stability_scores["aria_label"] = 0.90
        elif attributes.get("aria-labelledby"):
            selectors["aria_labelledby"] = f"[aria-labelledby='{attributes['aria-labelledby']}']"
            stability_scores["aria_labelledby"] = 0.85
        
        # Strategy 3: Semantic elements with role
        if attributes.get("role"):
            role_selector = f"[role='{attributes['role']}']"
            if attributes.get("name"):
                role_selector += f"[name='{attributes['name']}']"
            selectors["role_based"] = role_selector
            stability_scores["role_based"] = 0.80
        
        # Strategy 4: ID-based (good stability if meaningful)
        if attributes.get("id") and self._is_meaningful_id(attributes["id"]):
            selectors["id"] = f"#{attributes['id']}"
            stability_scores["id"] = 0.75
        
        # Strategy 5: CSS classes (less stable)
        if attributes.get("class"):
            classes = attributes["class"].split()
            meaningful_classes = [c for c in classes if self._is_meaningful_class(c)]
            if meaningful_classes:
                selectors["css_class"] = f".{'.'.join(meaningful_classes[:2])}"
                stability_scores["css_class"] = 0.60
        
        # Strategy 6: Text content (for buttons, links)
        if text_content and len(text_content.strip()) > 0:
            escaped_text = text_content.replace("'", "\\'")
            selectors["text_content"] = f"text='{escaped_text}'"
            stability_scores["text_content"] = 0.70
        
        # Strategy 7: XPath (fallback)
        if xpath:
            selectors["xpath"] = xpath
            stability_scores["xpath"] = 0.40
        
        # Strategy 8: CSS selector (fallback)
        if css_selector:
            selectors["css_selector"] = css_selector
            stability_scores["css_selector"] = 0.45
        
        # Select primary and fallback selectors
        primary_selector, primary_strategy = self._select_primary_selector(
            selectors, stability_scores
        )
        
        fallback_selectors = self._generate_fallback_selectors(
            selectors, stability_scores, primary_strategy
        )
        
        return {
            "primary": {
                "selector": primary_selector,
                "strategy": primary_strategy,
                "stability_score": stability_scores.get(primary_strategy, 0.0)
            },
            "fallbacks": fallback_selectors,
            "all_selectors": selectors,
            "stability_scores": stability_scores
        }
    
    def _is_meaningful_id(self, id_value: str) -> bool:
        """Check if an ID is meaningful and likely to be stable."""
        # Avoid auto-generated IDs
        meaningless_patterns = [
            r"^[a-f0-9]{8,}$",  # Long hex strings
            r"^uid_\d+$",       # UID patterns
            r"^id_\d+$",        # Simple ID patterns
            r"^\d+$",           # Pure numbers
        ]
        
        for pattern in meaningless_patterns:
            if re.match(pattern, id_value, re.IGNORECASE):
                return False
        
        return len(id_value) > 2
    
    def _is_meaningful_class(self, class_name: str) -> bool:
        """Check if a CSS class is meaningful and likely to be stable."""
        # Avoid utility classes and auto-generated classes
        meaningless_patterns = [
            r"^[a-f0-9]{6,}$",  # Hex color codes
            r"^css-\w+$",       # CSS-in-JS classes
            r"^sc-\w+$",        # Styled-components classes
            r"^_\w+$",          # Underscore-prefixed auto-generated
            r"^[A-Z0-9_]{10,}$" # Long uppercase auto-generated
        ]
        
        for pattern in meaningless_patterns:
            if re.match(pattern, class_name):
                return False
        
        # Prefer semantic class names
        semantic_keywords = [
            "button", "input", "form", "nav", "header", "footer", "content",
            "submit", "cancel", "primary", "secondary", "login", "menu"
        ]
        
        return any(keyword in class_name.lower() for keyword in semantic_keywords)
    
    def _select_primary_selector(self, selectors: Dict[str, str], 
                                stability_scores: Dict[str, float]) -> Tuple[str, str]:
        """Select the best primary selector based on strategy preferences and stability."""
        for strategy in self.config.preferred_strategies:
            strategy_key = strategy.value.replace("-", "_")
            if strategy_key in selectors:
                return selectors[strategy_key], strategy_key
        
        # If no preferred strategy found, use highest stability score
        if stability_scores:
            best_strategy = max(stability_scores.keys(), key=lambda k: stability_scores[k])
            return selectors[best_strategy], best_strategy
        
        # Last resort: use any available selector
        if selectors:
            first_key = next(iter(selectors.keys()))
            return selectors[first_key], first_key
        
        return "", ""
    
    def _generate_fallback_selectors(self, selectors: Dict[str, str],
                                   stability_scores: Dict[str, float],
                                   primary_strategy: str) -> List[Dict[str, Any]]:
        """Generate ordered fallback selectors."""
        fallbacks = []
        
        # Sort by stability score, excluding primary
        sorted_strategies = sorted(
            [(k, v, stability_scores.get(k, 0.0)) for k, v in selectors.items() if k != primary_strategy],
            key=lambda x: x[2],
            reverse=True
        )
        
        for strategy, selector, score in sorted_strategies[:3]:  # Limit to top 3 fallbacks
            fallbacks.append({
                "selector": selector,
                "strategy": strategy,
                "stability_score": score
            })
        
        return fallbacks


class RobustWaitGenerator:
    """Generates robust wait mechanisms with retry logic."""
    
    def __init__(self, config: WaitConfig):
        self.config = config
    
    def generate_wait_strategy(self, action_type: str, element_data: Dict[str, Any],
                             context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate appropriate wait strategy for an action.
        
        Args:
            action_type: Type of action being performed
            element_data: Element information
            context: Additional context about the page/application
            
        Returns:
            Wait strategy configuration
        """
        wait_strategies = []
        
        # Action-specific wait strategies
        if action_type in ["click", "click_element", "click_element_by_index"]:
            wait_strategies.extend([
                {
                    "type": WaitStrategy.ELEMENT_VISIBLE.value,
                    "timeout": self.config.default_timeout,
                    "description": "Wait for element to be visible and clickable"
                },
                {
                    "type": WaitStrategy.ELEMENT_STABLE.value,
                    "timeout": self.config.stability_check_duration,
                    "description": "Ensure element is stable before clicking"
                }
            ])
        
        elif action_type in ["input_text", "fill", "type"]:
            wait_strategies.extend([
                {
                    "type": WaitStrategy.ELEMENT_VISIBLE.value,
                    "timeout": self.config.default_timeout,
                    "description": "Wait for input field to be visible and enabled"
                }
            ])
        
        elif action_type in ["go_to_url", "navigate"]:
            wait_strategies.extend([
                {
                    "type": WaitStrategy.LOAD_STATE.value,
                    "state": "domcontentloaded",
                    "timeout": self.config.default_timeout,
                    "description": "Wait for DOM content to load"
                },
                {
                    "type": WaitStrategy.NETWORK_IDLE.value,
                    "timeout": self.config.network_idle_timeout,
                    "description": "Wait for network to be idle"
                }
            ])
        
        # Add custom wait conditions if specified
        if context and "wait_conditions" in context:
            for condition in context["wait_conditions"]:
                wait_strategies.append({
                    "type": WaitStrategy.CUSTOM_CONDITION.value,
                    "condition": condition,
                    "timeout": self.config.default_timeout,
                    "description": f"Custom wait condition: {condition}"
                })
        
        return {
            "strategies": wait_strategies,
            "retry_config": {
                "max_attempts": self.config.retry_attempts,
                "retry_delay": self.config.retry_delay,
                "exponential_backoff": True
            },
            "error_handling": {
                "capture_screenshot_on_timeout": True,
                "log_element_state": True,
                "alternative_selectors": True
            }
        }


class EnhancedAssertionGenerator:
    """Generates comprehensive assertions for test validation."""
    
    def __init__(self, config: AssertionConfig):
        self.config = config
    
    def generate_assertions(self, action_type: str, element_data: Dict[str, Any],
                          expected_result: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate appropriate assertions for an action.
        
        Args:
            action_type: Type of action performed
            element_data: Element information
            expected_result: Expected outcome of the action
            
        Returns:
            List of assertion configurations
        """
        assertions = []
        
        # Action-specific assertions
        if action_type in ["click", "click_element"]:
            assertions.extend([
                {
                    "type": "element_state",
                    "check": "visible",
                    "message": "Element should be visible before clicking",
                    "screenshot_on_failure": True
                },
                {
                    "type": "element_state", 
                    "check": "enabled",
                    "message": "Element should be enabled/clickable",
                    "screenshot_on_failure": True
                }
            ])
            
            # If it's a navigation action, check URL
            if expected_result and "expected_url" in expected_result:
                assertions.append({
                    "type": "url_contains",
                    "expected": expected_result["expected_url"],
                    "message": f"URL should contain '{expected_result['expected_url']}' after click",
                    "timeout": 10000
                })
        
        elif action_type in ["input_text", "fill"]:
            text_value = element_data.get("text", "")
            if text_value:
                assertions.append({
                    "type": "input_value",
                    "expected": text_value,
                    "message": f"Input should have value '{text_value}'",
                    "screenshot_on_failure": True
                })
        
        elif action_type in ["go_to_url", "navigate"]:
            url = element_data.get("url", "")
            if url:
                assertions.extend([
                    {
                        "type": "url_equals",
                        "expected": url,
                        "message": f"Should navigate to '{url}'",
                        "timeout": 15000
                    },
                    {
                        "type": "page_title",
                        "check": "not_empty",
                        "message": "Page should have a title",
                        "timeout": 5000
                    }
                ])
        
        # Add general page health assertions
        if self.config.auto_generate_assertions:
            assertions.extend([
                {
                    "type": "no_console_errors",
                    "message": "Page should not have console errors",
                    "severity": "warning"
                },
                {
                    "type": "no_404_requests",
                    "message": "Page should not have failed network requests",
                    "severity": "warning"
                }
            ])
        
        return assertions


class TestQualityAnalyzer:
    """Analyzes and scores test script quality."""
    
    def __init__(self):
        self.quality_rules = self._load_quality_rules()
    
    def analyze_test_script(self, script_content: str, 
                          metadata: Optional[Dict[str, Any]] = None) -> QualityMetrics:
        """
        Analyze test script and provide quality metrics.
        
        Args:
            script_content: Generated test script content
            metadata: Additional metadata about the generation process
            
        Returns:
            Quality metrics and recommendations
        """
        metrics = QualityMetrics()
        
        # Analyze selector quality
        metrics.selector_stability_score = self._analyze_selector_quality(script_content)
        
        # Analyze wait mechanisms
        metrics.wait_robustness_score = self._analyze_wait_robustness(script_content)
        
        # Analyze assertion coverage
        metrics.assertion_coverage_score = self._analyze_assertion_coverage(script_content)
        
        # Analyze maintainability
        metrics.maintainability_score = self._analyze_maintainability(script_content)
        
        # Calculate overall score
        metrics.overall_quality_score = (
            metrics.selector_stability_score * 0.3 +
            metrics.wait_robustness_score * 0.25 +
            metrics.assertion_coverage_score * 0.25 +
            metrics.maintainability_score * 0.2
        )
        
        # Generate recommendations
        metrics.recommendations = self._generate_recommendations(metrics, script_content)
        
        # Identify issues
        metrics.issues = self._identify_issues(script_content)
        
        return metrics
    
    def _analyze_selector_quality(self, script_content: str) -> float:
        """Analyze the quality of selectors used in the script."""
        score = 0.0
        total_selectors = 0
        
        # Look for different types of selectors
        selector_patterns = {
            "data_testid": (r'data-testid["\']', 0.95),
            "aria_label": (r'aria-label["\']', 0.90),
            "role": (r'role=["\']', 0.80),
            "id": (r'#[\w-]+', 0.75),
            "class": (r'\.[\w-]+', 0.60),
            "xpath": (r'//[^"\']*', 0.40),
            "css": (r'["\'][^"\']*\[[^"\']*\]["\']', 0.50)
        }
        
        for pattern_name, (pattern, weight) in selector_patterns.items():
            matches = re.findall(pattern, script_content)
            count = len(matches)
            total_selectors += count
            score += count * weight
        
        return score / max(total_selectors, 1)
    
    def _analyze_wait_robustness(self, script_content: str) -> float:
        """Analyze the robustness of wait mechanisms."""
        score = 0.5  # Base score
        
        # Check for explicit waits
        if re.search(r'wait_for[_\w]*\(', script_content):
            score += 0.3
        
        # Check for timeout specifications
        if re.search(r'timeout\s*[:=]\s*\d+', script_content):
            score += 0.2
        
        return min(score, 1.0)
    
    def _analyze_assertion_coverage(self, script_content: str) -> float:
        """Analyze assertion coverage in the script."""
        # Count different types of assertions
        assertion_patterns = [
            r'assert[_\w]*\(',
            r'expect\(',
            r'should[_\w]*\(',
            r'verify[_\w]*\('
        ]
        
        assertion_count = 0
        for pattern in assertion_patterns:
            assertion_count += len(re.findall(pattern, script_content))
        
        # Simple heuristic: more assertions = better coverage
        # Max score when we have 1+ assertion per 10 lines
        lines = len(script_content.split('\n'))
        ideal_assertions = max(lines // 10, 1)
        
        return min(assertion_count / ideal_assertions, 1.0)
    
    def _analyze_maintainability(self, script_content: str) -> float:
        """Analyze code maintainability."""
        score = 0.5  # Base score
        
        # Check for comments
        comment_lines = len(re.findall(r'^\s*#', script_content, re.MULTILINE))
        total_lines = len(script_content.split('\n'))
        if comment_lines / max(total_lines, 1) > 0.1:  # 10% comments
            score += 0.2
        
        # Check for function extraction
        if re.search(r'def\s+\w+\s*\(', script_content):
            score += 0.2
        
        # Check for constants/variables
        if re.search(r'^[A-Z_]+ = ', script_content, re.MULTILINE):
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendations(self, metrics: QualityMetrics, 
                                script_content: str) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        if metrics.selector_stability_score < 0.7:
            recommendations.append(
                "Consider using more stable selectors like data-testid or aria-label attributes"
            )
        
        if metrics.wait_robustness_score < 0.6:
            recommendations.append(
                "Add explicit wait conditions to improve test reliability"
            )
        
        if metrics.assertion_coverage_score < 0.5:
            recommendations.append(
                "Increase assertion coverage to validate test expectations"
            )
        
        if metrics.maintainability_score < 0.6:
            recommendations.append(
                "Add comments and extract reusable functions for better maintainability"
            )
        
        return recommendations
    
    def _identify_issues(self, script_content: str) -> List[str]:
        """Identify potential issues in the script."""
        issues = []
        
        # Check for hardcoded waits
        if re.search(r'sleep\s*\(\s*\d+', script_content):
            issues.append("Found hardcoded sleep() calls - consider using explicit waits instead")
        
        # Check for overly complex selectors
        complex_selectors = re.findall(r'["\'][^"\']{100,}["\']', script_content)
        if complex_selectors:
            issues.append(f"Found {len(complex_selectors)} overly complex selectors")
        
        # Check for missing error handling
        if not re.search(r'try\s*:', script_content) and not re.search(r'except\s*:', script_content):
            issues.append("No error handling found - consider adding try/except blocks")
        
        return issues
    
    def _load_quality_rules(self) -> Dict[str, Any]:
        """Load quality analysis rules."""
        # This could be loaded from a configuration file
        return {
            "selector_preferences": ["data-testid", "aria-label", "role", "id"],
            "required_waits": ["element_visible", "element_stable"],
            "assertion_types": ["visibility", "text_content", "url"],
            "maintainability_checks": ["comments", "functions", "constants"]
        }


class EnhancedTestQualitySystem:
    """Main system coordinating all test quality enhancements."""
    
    def __init__(self, selector_config: Optional[SelectorConfig] = None,
                 wait_config: Optional[WaitConfig] = None,
                 assertion_config: Optional[AssertionConfig] = None):
        self.selector_generator = SmartSelectorGenerator(
            selector_config or SelectorConfig()
        )
        self.wait_generator = RobustWaitGenerator(
            wait_config or WaitConfig()
        )
        self.assertion_generator = EnhancedAssertionGenerator(
            assertion_config or AssertionConfig()
        )
        self.quality_analyzer = TestQualityAnalyzer()
    
    def enhance_test_generation(self, automation_data: List[Dict[str, Any]],
                              context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance test generation with quality improvements.
        
        Args:
            automation_data: Original automation data
            context: Additional context for enhancement
            
        Returns:
            Enhanced generation configuration and recommendations
        """
        enhanced_steps = []
        
        for step_data in automation_data:
            enhanced_step = self._enhance_single_step(step_data, context)
            enhanced_steps.append(enhanced_step)
        
        # Generate overall quality recommendations
        quality_config = {
            "enhanced_steps": enhanced_steps,
            "quality_settings": {
                "use_smart_selectors": True,
                "use_robust_waits": True,
                "generate_assertions": True,
                "include_quality_comments": True
            },
            "global_recommendations": self._generate_global_recommendations(enhanced_steps)
        }
        
        return quality_config
    
    def _enhance_single_step(self, step_data: Dict[str, Any],
                           context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance a single automation step."""
        enhanced_step = step_data.copy()
        
        # Extract action and element information
        model_output = step_data.get("model_output", {})
        actions = model_output.get("action", [])
        state = step_data.get("state", {})
        interacted_elements = state.get("interacted_element", [])
        
        # Enhance each action
        enhanced_actions = []
        for action in actions:
            action_type = list(action.keys())[0] if action else ""
            action_data = action.get(action_type, {}) if action else {}
            
            # Find corresponding element data
            element_data = {}
            if "index" in action_data and interacted_elements:
                index = action_data.get("index", 0)
                if 0 <= index < len(interacted_elements):
                    element_data = interacted_elements[index]
            
            # Generate enhancements
            enhanced_action = {
                "original": action,
                "type": action_type,
                "selectors": self.selector_generator.generate_selector(element_data),
                "waits": self.wait_generator.generate_wait_strategy(action_type, element_data, context),
                "assertions": self.assertion_generator.generate_assertions(action_type, element_data),
                "quality_score": self._calculate_action_quality_score(action_type, element_data)
            }
            
            enhanced_actions.append(enhanced_action)
        
        enhanced_step["enhanced_actions"] = enhanced_actions
        return enhanced_step
    
    def _calculate_action_quality_score(self, action_type: str, 
                                      element_data: Dict[str, Any]) -> float:
        """Calculate quality score for a single action."""
        score = 0.5  # Base score
        
        # Check element stability indicators
        attributes = element_data.get("attributes", {})
        
        if attributes.get("data-testid"):
            score += 0.3
        elif attributes.get("aria-label"):
            score += 0.25
        elif attributes.get("id") and not re.match(r"^[a-f0-9]{8,}$", attributes["id"]):
            score += 0.15
        
        # Action-specific scoring
        if action_type in ["click", "input_text"] and attributes:
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_global_recommendations(self, enhanced_steps: List[Dict[str, Any]]) -> List[str]:
        """Generate global recommendations for the entire test."""
        recommendations = []
        
        # Analyze overall selector quality
        total_actions = sum(len(step.get("enhanced_actions", [])) for step in enhanced_steps)
        high_quality_selectors = sum(
            1 for step in enhanced_steps
            for action in step.get("enhanced_actions", [])
            if action.get("quality_score", 0) > 0.8
        )
        
        if total_actions > 0:
            quality_ratio = high_quality_selectors / total_actions
            if quality_ratio < 0.6:
                recommendations.append(
                    "Consider adding data-testid attributes to improve selector stability"
                )
        
        # Check for missing wait strategies
        actions_with_waits = sum(
            1 for step in enhanced_steps
            for action in step.get("enhanced_actions", [])
            if action.get("waits", {}).get("strategies", [])
        )
        
        if actions_with_waits < total_actions * 0.8:
            recommendations.append(
                "Add explicit wait conditions for better test reliability"
            )
        
        return recommendations
    
    def analyze_generated_script(self, script_content: str,
                               metadata: Optional[Dict[str, Any]] = None) -> QualityMetrics:
        """Analyze the quality of a generated test script."""
        return self.quality_analyzer.analyze_test_script(script_content, metadata) 