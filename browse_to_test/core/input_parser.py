"""
Input parser for browser automation data.

Handles parsing and normalizing various formats of browser automation data
into a standardized internal format for processing.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from pathlib import Path


logger = logging.getLogger(__name__)


@dataclass
class ParsedAction:
    """Represents a single parsed action from browser automation data."""
    
    action_type: str  # go_to_url, click_element, input_text, etc.
    parameters: Dict[str, Any]  # Action-specific parameters
    step_index: int  # Which step this action belongs to
    action_index: int  # Index within the step
    selector_info: Optional[Dict[str, Any]] = None  # Element selector information
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
    
    def __post_init__(self):
        """Ensure parameters and metadata are not None."""
        if self.parameters is None:
            self.parameters = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ParsedStep:
    """Represents a single parsed step containing one or more actions."""
    
    step_index: int
    actions: List[ParsedAction]
    step_metadata: Optional[Dict[str, Any]] = None
    timing_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Ensure metadata is not None."""
        if self.step_metadata is None:
            self.step_metadata = {}
        if self.timing_info is None:
            self.timing_info = {}


@dataclass
class ParsedAutomationData:
    """Container for all parsed automation data."""
    
    steps: List[ParsedStep]
    total_actions: int
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Calculate total actions and ensure metadata is not None."""
        if self.metadata is None:
            self.metadata = {}
        
        # Recalculate total actions from steps
        self.total_actions = sum(len(step.actions) for step in self.steps)


class InputParser:
    """Parser for browser automation data from various sources."""
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the input parser.
        
        Args:
            strict_mode: If True, raise exceptions on parsing errors.
                        If False, log warnings and skip invalid data.
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(__name__)
    
    def parse(self, automation_data: Union[List[Dict], str, Path]) -> ParsedAutomationData:
        """
        Parse browser automation data from various input formats.
        
        Args:
            automation_data: Can be:
                - List of step dictionaries (direct format)
                - JSON string containing the data
                - Path to JSON file containing the data
                
        Returns:
            ParsedAutomationData containing normalized data
            
        Raises:
            ValueError: If data format is invalid and strict_mode is True
        """
        # Handle different input types
        if isinstance(automation_data, (str, Path)):
            automation_data = self._load_from_file_or_string(automation_data)
        
        if not isinstance(automation_data, list):
            error_msg = f"Expected list of steps, got {type(automation_data)}"
            if self.strict_mode:
                raise ValueError(error_msg)
            self.logger.warning(error_msg)
            return ParsedAutomationData(steps=[], total_actions=0)
        
        # Parse each step
        parsed_steps = []
        for step_index, step_data in enumerate(automation_data):
            try:
                parsed_step = self._parse_step(step_data, step_index)
                if parsed_step.actions:  # Only add steps with valid actions
                    parsed_steps.append(parsed_step)
            except Exception as e:
                error_msg = f"Error parsing step {step_index}: {e}"
                if self.strict_mode:
                    raise ValueError(error_msg) from e
                self.logger.warning(error_msg)
                continue
        
        total_actions = sum(len(step.actions) for step in parsed_steps)
        
        self.logger.info(
            f"Parsed {len(parsed_steps)} steps with {total_actions} total actions"
        )
        
        return ParsedAutomationData(
            steps=parsed_steps,
            total_actions=total_actions,
            metadata={
                "original_step_count": len(automation_data),
                "parsed_step_count": len(parsed_steps),
                "parser_version": "1.0.0"
            }
        )
    
    def _load_from_file_or_string(self, data: Union[str, Path]) -> List[Dict]:
        """Load automation data from file path or JSON string."""
        if isinstance(data, Path) or (isinstance(data, str) and Path(data).exists()):
            # Load from file
            file_path = Path(data)
            if not file_path.exists():
                raise FileNotFoundError(f"Automation data file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Try to parse as JSON string
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string provided: {e}")
    
    def _parse_step(self, step_data: Dict[str, Any], step_index: int) -> ParsedStep:
        """Parse a single step from the automation data."""
        if not isinstance(step_data, dict):
            raise ValueError(f"Step {step_index} is not a dictionary")
        
        # Extract step metadata
        step_metadata = {
            key: value for key, value in step_data.items() 
            if key not in ['model_output', 'state']
        }
        
        # Extract timing information if available
        timing_info = {}
        if 'metadata' in step_data and isinstance(step_data['metadata'], dict):
            metadata = step_data['metadata']
            timing_fields = ['step_start_time', 'step_end_time', 'elapsed_time']
            timing_info = {
                field: metadata.get(field) 
                for field in timing_fields 
                if field in metadata
            }
        
        # Get model output containing actions
        model_output = step_data.get('model_output', {})
        if not isinstance(model_output, dict):
            self.logger.warning(f"Step {step_index} has invalid model_output")
            return ParsedStep(step_index, [], step_metadata, timing_info)
        
        # Extract actions
        actions_data = model_output.get('action', [])
        if not isinstance(actions_data, list):
            self.logger.warning(f"Step {step_index} has invalid actions format")
            return ParsedStep(step_index, [], step_metadata, timing_info)
        
        # Parse each action
        parsed_actions = []
        state_data = step_data.get('state', {})
        interacted_elements = state_data.get('interacted_element', [])
        
        for action_index, action_data in enumerate(actions_data):
            try:
                parsed_action = self._parse_action(
                    action_data, 
                    step_index, 
                    action_index,
                    interacted_elements
                )
                if parsed_action:
                    parsed_actions.append(parsed_action)
            except Exception as e:
                error_msg = f"Error parsing action {action_index} in step {step_index}: {e}"
                if self.strict_mode:
                    raise ValueError(error_msg) from e
                self.logger.warning(error_msg)
                continue
        
        return ParsedStep(
            step_index=step_index,
            actions=parsed_actions,
            step_metadata=step_metadata,
            timing_info=timing_info
        )
    
    def _parse_action(
        self, 
        action_data: Dict[str, Any], 
        step_index: int, 
        action_index: int,
        interacted_elements: List[Dict[str, Any]]
    ) -> Optional[ParsedAction]:
        """Parse a single action from the action data."""
        if not isinstance(action_data, dict) or not action_data:
            self.logger.warning(f"Empty or invalid action at step {step_index}, action {action_index}")
            return None
        
        # Extract action type (first key in the dictionary)
        action_type = next(iter(action_data.keys()))
        parameters = action_data[action_type]
        
        if not isinstance(parameters, dict):
            if parameters is None:
                parameters = {}
            else:
                self.logger.warning(
                    f"Action {action_type} has invalid parameters at step {step_index}, action {action_index}"
                )
                return None
        
        # Extract selector information if available
        selector_info = None
        if action_index < len(interacted_elements) and interacted_elements[action_index]:
            selector_info = self._extract_selector_info(interacted_elements[action_index])
        
        # Create action metadata
        action_metadata = {
            'original_format': 'browser_automation',
            'requires_element': self._requires_element_interaction(action_type),
            'has_selector': selector_info is not None
        }
        
        return ParsedAction(
            action_type=action_type,
            parameters=parameters,
            step_index=step_index,
            action_index=action_index,
            selector_info=selector_info,
            metadata=action_metadata
        )
    
    def _extract_selector_info(self, element_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize selector information from element data."""
        selector_info = {}
        
        # Extract XPath
        if 'xpath' in element_data and element_data['xpath']:
            xpath = element_data['xpath']
            # Normalize XPath format
            if not xpath.startswith('xpath=') and not xpath.startswith('/'):
                xpath = f'//{xpath}'
            if not xpath.startswith('xpath=') and xpath.startswith('/'):
                xpath = f'xpath={xpath}'
            selector_info['xpath'] = xpath
        
        # Extract CSS selector
        if 'css_selector' in element_data and element_data['css_selector']:
            selector_info['css_selector'] = element_data['css_selector']
        
        # Extract other useful information
        if 'highlight_index' in element_data:
            selector_info['highlight_index'] = element_data['highlight_index']
        
        # Extract element attributes if available
        if 'attributes' in element_data:
            selector_info['attributes'] = element_data['attributes']
        
        # Extract text content if available
        if 'text_content' in element_data:
            selector_info['text_content'] = element_data['text_content']
        
        return selector_info
    
    def _requires_element_interaction(self, action_type: str) -> bool:
        """Determine if an action type requires element interaction."""
        element_actions = {
            'click_element', 'click_element_by_index', 'input_text', 
            'click_download_button', 'drag_drop', 'hover_element'
        }
        return action_type in element_actions
    
    def validate_parsed_data(self, parsed_data: ParsedAutomationData) -> List[str]:
        """
        Validate parsed automation data and return list of validation issues.
        
        Args:
            parsed_data: The parsed automation data to validate
            
        Returns:
            List of validation warning/error messages
        """
        issues = []
        
        if not parsed_data.steps:
            issues.append("No valid steps found in automation data")
            return issues
        
        if parsed_data.total_actions == 0:
            issues.append("No valid actions found in automation data")
        
        # Check each step
        for step in parsed_data.steps:
            step_prefix = f"Step {step.step_index}"
            
            if not step.actions:
                issues.append(f"{step_prefix}: No valid actions found")
                continue
            
            # Check for actions that require selectors but don't have them
            for action in step.actions:
                action_prefix = f"{step_prefix}, Action {action.action_index}"
                
                if action.metadata.get('requires_element') and not action.metadata.get('has_selector'):
                    issues.append(
                        f"{action_prefix}: Action '{action.action_type}' requires element "
                        "selector but none was found"
                    )
                
                # Check for empty parameters on actions that typically need them
                if action.action_type in ['go_to_url', 'input_text', 'search_google']:
                    if not action.parameters:
                        issues.append(
                            f"{action_prefix}: Action '{action.action_type}' has no parameters"
                        )
        
        return issues
    
    def extract_sensitive_data_keys(self, parsed_data: ParsedAutomationData) -> List[str]:
        """
        Extract potential sensitive data keys from the parsed data.
        
        Looks for patterns like <secret>key</secret> in action parameters.
        
        Args:
            parsed_data: The parsed automation data
            
        Returns:
            List of unique sensitive data keys found
        """
        import re
        
        sensitive_keys = set()
        secret_pattern = re.compile(r'<secret>([^<]+)</secret>')
        
        for step in parsed_data.steps:
            for action in step.actions:
                # Check all string values in parameters
                for param_name, param_value in action.parameters.items():
                    if isinstance(param_value, str):
                        matches = secret_pattern.findall(param_value)
                        sensitive_keys.update(matches)
        
        return sorted(list(sensitive_keys)) 