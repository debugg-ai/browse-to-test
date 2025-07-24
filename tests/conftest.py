"""Pytest configuration and fixtures for browse-to-test tests."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock

import pytest
from faker import Faker

import browse_to_test as btt
from browse_to_test.ai.base import AIResponse, AIProvider
from browse_to_test.core.processing.context_collector import SystemContext, ProjectContext, TestFileInfo
from browse_to_test.core.processing.input_parser import ParsedAutomationData


collect_ignore = [
    "browse_to_test/language_utils",
    "browse_to_test/core",
    "examples",
    "script_generators",
    "training_data",
]

# Initialize faker for generating test data
fake = Faker()


@pytest.fixture
def sample_automation_data() -> List[Dict[str, Any]]:
    """Sample browser automation data for testing."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://example.com"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "elapsed_time": 1.2
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "test@example.com",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@data-testid='email-input']",
                        "css_selector": "input[data-testid='email-input']",
                        "attributes": {
                            "id": "email",
                            "name": "email",
                            "data-testid": "email-input",
                            "type": "email"
                        },
                        "text_content": ""
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "click_element": {
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//button[@type='submit']",
                        "css_selector": "button[type='submit']",
                        "attributes": {
                            "type": "submit",
                            "class": "btn btn-primary"
                        },
                        "text_content": "Submit"
                    }
                ]
            }
        }
    ]


@pytest.fixture
def complex_automation_data() -> List[Dict[str, Any]]:
    """Complex automation data with edge cases."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://complex-app.example.com/login"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "<secret>username</secret>",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@id='username-field']",
                        "css_selector": "#username-field",
                        "attributes": {
                            "id": "username-field",
                            "name": "username",
                            "data-testid": "username-input",
                            "type": "text",
                            "placeholder": "Enter username",
                            "required": True
                        }
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "<secret>password</secret>",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@type='password']",
                        "css_selector": "input[type='password']",
                        "attributes": {
                            "type": "password",
                            "name": "password",
                            "data-testid": "password-input"
                        }
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "wait": {
                            "seconds": 2
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "click_element": {
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//button[contains(text(), 'Login')]",
                        "css_selector": "button.login-btn",
                        "attributes": {
                            "type": "submit",
                            "class": "login-btn btn-primary",
                            "data-testid": "login-submit"
                        },
                        "text_content": "Login"
                    }
                ]
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "text": "Successfully logged in",
                            "success": True
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        }
    ]


@pytest.fixture
def invalid_automation_data() -> List[Dict[str, Any]]:
    """Invalid automation data for testing error handling."""
    return [
        {
            "model_output": {
                "action": []  # Empty actions
            },
            "state": {
                "interacted_element": []
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "invalid_action": {
                            "invalid_param": "invalid_value"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            }
        },
        {
            # Missing model_output
            "state": {
                "interacted_element": []
            }
        }
    ]


@pytest.fixture
def basic_config() -> btt.Config:
    """Basic configuration for testing."""
    return btt.Config(
        ai=btt.AIConfig(
            provider="mock",
            model="mock-model",
            api_key="mock-key"
        ),
        output=btt.OutputConfig(
            framework="playwright",
            language="python"
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=False,
            collect_system_context=False
        )
    )


@pytest.fixture
def context_enabled_config() -> btt.Config:
    """Configuration with context collection enabled."""
    return btt.Config(
        ai=btt.AIConfig(
            provider="mock",
            model="mock-model",
            api_key="mock-key"
        ),
        output=btt.OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_error_handling=True
        ),
        processing=btt.ProcessingConfig(
            analyze_actions_with_ai=True,
            collect_system_context=True,
            use_intelligent_analysis=True,
            include_existing_tests=True,
            include_documentation=True,
            context_analysis_depth="medium"
        ),
        project_root="/tmp/test_project"
    )


@pytest.fixture
def mock_ai_provider() -> Mock:
    """Mock AI provider for testing."""
    provider = Mock(spec=AIProvider)
    provider.generate.return_value = AIResponse(
        content="Mock AI response",
        model="mock-model",
        provider="mock",
        tokens_used=100
    )
    provider.analyze_with_context.return_value = AIResponse(
        content="Mock analysis response",
        model="mock-model",
        provider="mock",
        tokens_used=150
    )
    provider.is_available.return_value = True
    provider.get_model_info.return_value = {
        "name": "mock-model",
        "provider": "mock",
        "max_tokens": 4000
    }
    return provider


@pytest.fixture
def sample_system_context() -> SystemContext:
    """Sample system context for testing."""
    project = ProjectContext(
        project_root="/tmp/test_project",
        name="test-project",
        description="A test project",
        tech_stack=["react", "typescript", "playwright"],
        test_frameworks=["playwright", "jest"]
    )
    
    test_files = [
        TestFileInfo(
            file_path="tests/login.spec.ts",
            framework="playwright",
            language="typescript",
            test_functions=["test login flow", "test invalid credentials"],
            selectors=["[data-testid='username']", "[data-testid='password']"],
            actions=["goto", "fill", "click"],
            assertions=["toBeVisible", "toContainText"],
            imports=["@playwright/test"],
            last_modified=fake.date_time(),
            size_bytes=1024
        ),
        TestFileInfo(
            file_path="tests/signup.spec.ts",
            framework="playwright",
            language="typescript",
            test_functions=["test signup flow"],
            selectors=["#email", "#password", "#confirm-password"],
            actions=["goto", "fill", "click"],
            assertions=["toBeVisible"],
            imports=["@playwright/test"],
            last_modified=fake.date_time(),
            size_bytes=512
        )
    ]
    
    return SystemContext(
        project=project,
        existing_tests=test_files,
        documentation={"README.md": "# Test Project\nA sample project for testing"},
        ui_components={"Button.tsx": {"component_names": ["Button"], "props": ["onClick", "children"]}},
        api_endpoints=[{"method": "POST", "path": "/api/login"}]
    )


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        
        # Create directory structure
        (project_path / "tests").mkdir()
        (project_path / "src" / "components").mkdir(parents=True)
        (project_path / "docs").mkdir()
        
        # Create test files
        (project_path / "tests" / "login.spec.ts").write_text("""
import { test, expect } from '@playwright/test';

test('login flow', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-testid="username"]', 'testuser');
  await page.fill('[data-testid="password"]', 'password');
  await page.click('[data-testid="login-submit"]');
  await expect(page).toHaveURL('/dashboard');
});
        """)
        
        (project_path / "tests" / "signup.spec.ts").write_text("""
import { test, expect } from '@playwright/test';

test('signup flow', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('#email', 'test@example.com');
  await page.fill('#password', 'password123');
  await page.click('button[type="submit"]');
});
        """)
        
        # Create component files
        (project_path / "src" / "components" / "Button.tsx").write_text("""
import React from 'react';

interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ onClick, children, disabled }) => (
  <button onClick={onClick} disabled={disabled} className="btn">
    {children}
  </button>
);
        """)
        
        # Create documentation
        (project_path / "README.md").write_text("""
# Test Project

A sample project for testing the browse-to-test library.

## Features

- User authentication
- Component library
- Test automation
        """)
        
        # Create package.json
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "description": "A test project",
            "dependencies": {
                "react": "^18.0.0",
                "typescript": "^5.0.0"
            },
            "devDependencies": {
                "@playwright/test": "^1.30.0",
                "jest": "^29.0.0"
            }
        }
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        
        yield project_path


@pytest.fixture
def parsed_automation_data(sample_automation_data) -> ParsedAutomationData:
    """Parsed automation data for testing."""
    parser = btt.InputParser(btt.Config())
    return parser.parse(sample_automation_data)


@pytest.fixture
def edge_case_data() -> List[Dict[str, Any]]:
    """Edge case data for testing robustness."""
    return [
        # Missing state
        {
            "model_output": {
                "action": [{"go_to_url": {"url": "https://example.com"}}]
            }
        },
        # Missing action parameters
        {
            "model_output": {
                "action": [{"click_element": {}}]
            },
            "state": {"interacted_element": []}
        },
        # Malformed selector info
        {
            "model_output": {
                "action": [{"input_text": {"text": "test", "index": 0}}]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": None,
                        "css_selector": "",
                        "attributes": {}
                    }
                ]
            }
        },
        # Very long text content
        {
            "model_output": {
                "action": [{"input_text": {"text": "x" * 10000, "index": 0}}]
            },
            "state": {"interacted_element": []}
        },
        # Unicode and special characters
        {
            "model_output": {
                "action": [{"input_text": {"text": "🚀 Test with émojis and spëcial chars 中文", "index": 0}}]
            },
            "state": {"interacted_element": []}
        }
    ]


@pytest.fixture(autouse=True)
def clean_environment():
    """Clean environment variables before each test."""
    # Store original values
    original_env = {}
    test_env_vars = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
        "BROWSE_TO_TEST_AI_PROVIDER",
        "BROWSE_TO_TEST_OUTPUT_FRAMEWORK",
        "BROWSE_TO_TEST_DEBUG"
    ]
    
    for var in test_env_vars:
        if var in os.environ:
            original_env[var] = os.environ[var]
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_env.items():
        os.environ[var] = value


@pytest.fixture
def mock_file_system(tmp_path):
    """Mock file system for testing file operations."""
    # Create a mock project structure
    test_dir = tmp_path / "tests"
    test_dir.mkdir()
    
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    # Create mock files
    (test_dir / "test_example.py").write_text("""
import pytest

def test_something():
    assert True
    """)
    
    (src_dir / "__init__.py").write_text("")
    
    return tmp_path


@pytest.fixture
def mock_responses():
    """Mock HTTP responses for testing network interactions."""
    import responses
    
    with responses.RequestsMock() as rsps:
        # Mock OpenAI API
        rsps.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json={
                "choices": [{"message": {"content": "Mock OpenAI response"}}],
                "usage": {"total_tokens": 100}
            }
        )
        
        # Mock Anthropic API
        rsps.add(
            responses.POST,
            "https://api.anthropic.com/v1/messages",
            json={
                "content": [{"text": "Mock Anthropic response"}],
                "usage": {"input_tokens": 50, "output_tokens": 50}
            }
        )
        
        yield rsps


# Parametrized fixtures for testing multiple scenarios
@pytest.fixture(params=["playwright", "selenium"])
def framework(request):
    """Parametrized fixture for testing multiple frameworks."""
    return request.param


@pytest.fixture(params=["python", "javascript", "typescript"])
def language(request):
    """Parametrized fixture for testing multiple languages."""
    return request.param


@pytest.fixture(params=["openai", "anthropic", "mock"])
def ai_provider(request):
    """Parametrized fixture for testing multiple AI providers."""
    return request.param


# Performance testing fixtures
@pytest.fixture
def large_automation_data():
    """Large automation data for performance testing."""
    actions = []
    for i in range(100):
        actions.append({
            "model_output": {
                "action": [
                    {
                        "click_element": {
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": f"//button[@id='btn-{i}']",
                        "css_selector": f"#btn-{i}",
                        "attributes": {"id": f"btn-{i}"}
                    }
                ]
            }
        })
    return actions


@pytest.fixture
def stress_test_config():
    """Configuration for stress testing."""
    return btt.Config(
        processing=btt.ProcessingConfig(
            max_cache_size=1000,
            context_cache_ttl=60,
            max_context_files=500
        )
    ) 