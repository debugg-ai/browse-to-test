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

from ..configuration.config import Config


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
        """Ensure parameters is not None."""
        if self.parameters is None:
            self.parameters = {}
        # Don't automatically set metadata to {} - let it stay None if not provided
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedAction':
        """Create ParsedAction from dictionary."""
        return cls(
            action_type=data.get('action_type', ''),
            parameters=data.get('parameters', {}),
            step_index=data.get('step_index', 0),
            action_index=data.get('action_index', 0),
            selector_info=data.get('selector_info'),
            metadata=data.get('metadata')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ParsedAction to dictionary."""
        return {
            'action_type': self.action_type,
            'parameters': self.parameters,
            'step_index': self.step_index,
            'action_index': self.action_index,
            'selector_info': self.selector_info,
            'metadata': self.metadata
        }


@dataclass
class ParsedStep:
    """Represents a single parsed step containing one or more actions."""
    
    step_index: int
    actions: List[ParsedAction]
    metadata: Optional[Dict[str, Any]] = None
    timing_info: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Post-initialization processing for ParsedStep."""
        # Don't automatically set timing_info or metadata to {} - let them stay None if not provided
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ParsedStep':
        """Create ParsedStep from dictionary."""
        actions_data = data.get('actions', [])
        actions = []
        for action_data in actions_data:
            if isinstance(action_data, dict):
                actions.append(ParsedAction.from_dict(action_data))
            else:
                actions.append(action_data)  # Already a ParsedAction
        
        return cls(
            step_index=data.get('step_index', 0),
            actions=actions,
            metadata=data.get('metadata'),
            timing_info=data.get('timing_info')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ParsedStep to dictionary."""
        return {
            'step_index': self.step_index,
            'actions': [action.to_dict() if hasattr(action, 'to_dict') else action.__dict__ for action in self.actions],
            'metadata': self.metadata,
            'timing_info': self.timing_info
        }


@dataclass
class ParsedAutomationData:
    """Container for all parsed automation data."""
    
    steps: List[ParsedStep]
    total_actions: int = 0  # Will be calculated in __post_init__
    sensitive_data_keys: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Calculate total actions from steps if not provided."""
        if self.sensitive_data_keys is None:
            self.sensitive_data_keys = []
        
        # Recalculate total actions from steps
        self.total_actions = sum(len(step.actions) for step in self.steps)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the parsed data to a dictionary format."""
        return {
            "steps": [step.to_dict() if hasattr(step, 'to_dict') else step.__dict__ for step in self.steps],
            "total_actions": self.total_actions,
            "sensitive_data_keys": self.sensitive_data_keys or [],
            "metadata": self.metadata or {}
        }


class InputParser:
    """Parser for browser automation data from various sources."""
    
    def __init__(self, config):
        """
        Initialize the input parser.
        
        Args:
            config: Configuration object containing parsing settings.
        """
        self.config = config
        self.strict_mode = config.processing.strict_mode
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
        # Handle None input
        if automation_data is None:
            raise ValueError("Automation data cannot be None")
        
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
                parsed_steps.append(parsed_step)  # Include all steps, even empty ones
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
        # Handle Path objects
        if isinstance(data, Path):
            if not data.exists():
                raise FileNotFoundError(f"Automation data file not found: {data}")
            with open(data, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Handle string inputs
        if isinstance(data, str):
            # Check if it looks like a file path - be more restrictive
            # Must not start with [ or { (JSON indicators) and should be a reasonable file path
            is_potential_file = (
                not data.strip().startswith(('[', '{')) and
                len(data) < 500 and  # File paths are usually not very long
                (data.endswith('.json') or ('/' in data and not 'http' in data))
            )
            
            if is_potential_file:
                file_path = Path(data)
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    raise FileNotFoundError(f"Automation data file not found: {file_path}")
            
            # Try to parse as JSON string
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # Re-raise the original JSONDecodeError for tests that expect it
                raise
        
        raise ValueError(f"Unsupported data type: {type(data)}")
    
    def _parse_step(self, step_data: Dict[str, Any], step_index: int) -> ParsedStep:
        """Parse a single step from the automation data."""
        if not isinstance(step_data, dict):
            raise ValueError(f"Step {step_index} is not a dictionary")
        
        # Check for required fields - model_output is required for valid automation data
        if 'model_output' not in step_data:
            if self.strict_mode:
                raise ValueError(f"Step {step_index} is missing required 'model_output' field")
            self.logger.warning(f"Step {step_index} is missing required 'model_output' field")
            return ParsedStep(step_index=step_index, actions=[], metadata={}, timing_info={})
        
        # Extract step metadata - use the metadata field directly if available
        step_metadata = None
        if 'metadata' in step_data and isinstance(step_data['metadata'], dict):
            step_metadata = step_data['metadata'].copy()
        
        # Also include any other fields that aren't model_output, state, or metadata
        other_fields = {key: value for key, value in step_data.items() 
                       if key not in ['model_output', 'state', 'metadata']}
        
        if other_fields:
            if step_metadata is None:
                step_metadata = other_fields
            else:
                step_metadata.update(other_fields)
        
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
            if self.strict_mode:
                raise ValueError(f"Step {step_index} has invalid model_output type: {type(model_output)}")
            self.logger.warning(f"Step {step_index} has invalid model_output")
            return ParsedStep(step_index=step_index, actions=[], metadata=step_metadata, timing_info=timing_info)
        
        # Extract actions
        actions_data = model_output.get('action', [])
        if not isinstance(actions_data, list):
            self.logger.warning(f"Step {step_index} has invalid actions format")
            return ParsedStep(step_index=step_index, actions=[], metadata=step_metadata, timing_info=timing_info)
        
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
            metadata=step_metadata,
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
            # Store the xpath as-is without normalization
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