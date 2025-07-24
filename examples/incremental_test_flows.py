#!/usr/bin/env python3
"""
Example test flows demonstrating incremental test script generation.

This module provides several example flows that showcase the live update
functionality of the browse-to-test incremental system.
"""

import asyncio
import json
from typing import List, Dict, Any, Callable
from pathlib import Path

from browse_to_test.core.orchestration.incremental_orchestrator import (
    btt.IncrementalSession,
    IncrementalUpdateResult
)
from browse_to_test.core.configuration.config import Config, OutputConfig, ProcessingConfig


class IncrementalTestFlowRunner:
    """Runner for incremental test flows with real-time updates."""
    
    def __init__(self, config: Config):
        self.orchestrator = btt.IncrementalSession(config)
        self.update_history: List[IncrementalUpdateResult] = []
        
        # Register callback to track updates
        self.orchestrator.register_update_callback(self._track_update)
    
    def _track_update(self, result: IncrementalUpdateResult):
        """Track updates for analysis."""
        self.update_history.append(result)
        print(f"📊 Update: {result.new_lines_added} lines added, "
              f"Success: {result.success}, "
              f"Issues: {len(result.validation_issues)}")
    
    async def run_flow(
        self, 
        flow_name: str, 
        steps: List[Dict[str, Any]], 
        target_url: str = None,
        context_hints: Dict[str, Any] = None,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        Run a complete incremental test flow.
        
        Args:
            flow_name: Name of the test flow
            steps: List of automation steps to process
            target_url: Target URL for the test
            context_hints: Context hints for the test
            show_progress: Whether to show progress updates
            
        Returns:
            Dictionary with flow results and statistics
        """
        if show_progress:
            print(f"\n🚀 Starting incremental flow: {flow_name}")
            print(f"📍 Target URL: {target_url}")
            print(f"📋 Steps to process: {len(steps)}")
            print("-" * 60)
        
        self.update_history.clear()
        
        try:
            # Phase 1: Setup
            if show_progress:
                print("🔧 Phase 1: Setting up incremental session...")
            
            setup_result = self.orchestrator.start_incremental_session(
                target_url=target_url,
                context_hints=context_hints
            )
            
            if not setup_result.success:
                return {
                    "flow_name": flow_name,
                    "success": False,
                    "error": "Setup failed",
                    "setup_issues": setup_result.validation_issues
                }
            
            if show_progress:
                print(f"✅ Setup complete: {setup_result.new_lines_added} lines generated")
                print(f"📝 Script preview:\n{setup_result.updated_script[:200]}...\n")
            
            # Phase 2: Incremental steps
            if show_progress:
                print("⚡ Phase 2: Processing steps incrementally...")
            
            step_results = []
            for i, step in enumerate(steps):
                if show_progress:
                    print(f"  📦 Processing step {i + 1}/{len(steps)}...")
                
                step_result = self.orchestrator.add_step(step, analyze_step=True)
                step_results.append(step_result)
                
                if not step_result.success:
                    if show_progress:
                        print(f"  ❌ Step {i + 1} failed: {step_result.validation_issues}")
                    break
                
                if show_progress and step_result.analysis_insights:
                    print(f"  💡 Insights: {step_result.analysis_insights[:2]}")
                
                # Simulate real-time delay
                await asyncio.sleep(0.1)
            
            # Phase 3: Finalization
            if show_progress:
                print("\n🏁 Phase 3: Finalizing script...")
            
            final_result = self.orchestrator.finalize_session(
                final_validation=True,
                optimize_script=True
            )
            
            if show_progress:
                if final_result.success:
                    print("✅ Finalization complete!")
                else:
                    print(f"❌ Finalization issues: {final_result.validation_issues}")
            
            # Generate summary
            summary = {
                "flow_name": flow_name,
                "success": final_result.success,
                "total_steps_processed": len(step_results),
                "successful_steps": sum(1 for r in step_results if r.success),
                "total_updates": len(self.update_history),
                "final_script_lines": len(final_result.updated_script.split('\n')),
                "validation_issues": final_result.validation_issues,
                "optimization_insights": final_result.analysis_insights,
                "final_script": final_result.updated_script,
                "update_history": [
                    {
                        "lines_added": u.new_lines_added,
                        "success": u.success,
                        "issues_count": len(u.validation_issues),
                        "insights_count": len(u.analysis_insights)
                    }
                    for u in self.update_history
                ]
            }
            
            if show_progress:
                print(f"\n📊 Flow Summary:")
                print(f"  • Total steps: {summary['total_steps_processed']}")
                print(f"  • Successful: {summary['successful_steps']}")
                print(f"  • Final script: {summary['final_script_lines']} lines")
                print(f"  • Validation issues: {len(summary['validation_issues'])}")
                print(f"  • Success: {summary['success']}")
            
            return summary
            
        except Exception as e:
            return {
                "flow_name": flow_name,
                "success": False,
                "error": str(e),
                "update_history": self.update_history
            }


# Test Flow Definitions

def get_login_flow_steps() -> List[Dict[str, Any]]:
    """Generate steps for a login flow test."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://example.com/login"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "elapsed_time": 1.2,
                "description": "Navigate to login page"
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
                        "xpath": "//input[@data-testid='username-input']",
                        "css_selector": "input[data-testid='username-input']",
                        "attributes": {
                            "id": "username",
                            "name": "username",
                            "data-testid": "username-input",
                            "type": "email",
                            "placeholder": "Enter your email"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995201.2,
                "elapsed_time": 0.8,
                "description": "Enter username"
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
                        "xpath": "//input[@data-testid='password-input']",
                        "css_selector": "input[data-testid='password-input']",
                        "attributes": {
                            "id": "password",
                            "name": "password",
                            "data-testid": "password-input",
                            "type": "password",
                            "placeholder": "Enter your password"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995202.0,
                "elapsed_time": 0.6,
                "description": "Enter password"
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
                        "xpath": "//button[@data-testid='login-button']",
                        "css_selector": "button[data-testid='login-button']",
                        "attributes": {
                            "data-testid": "login-button",
                            "type": "submit",
                            "class": "btn btn-primary"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995202.6,
                "elapsed_time": 0.4,
                "description": "Click login button"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "wait": {
                            "seconds": 3
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995203.0,
                "elapsed_time": 3.0,
                "description": "Wait for login to complete"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "success": True,
                            "text": "Login flow completed successfully"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995206.0,
                "elapsed_time": 0.1,
                "description": "Mark test as complete"
            }
        }
    ]


def get_shopping_cart_flow_steps() -> List[Dict[str, Any]]:
    """Generate steps for a shopping cart flow test."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://shop.example.com"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "elapsed_time": 2.1,
                "description": "Navigate to shop"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "laptop",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@data-testid='search-input']",
                        "css_selector": "input[data-testid='search-input']",
                        "attributes": {
                            "data-testid": "search-input",
                            "placeholder": "Search products...",
                            "type": "text"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995202.1,
                "elapsed_time": 0.5,
                "description": "Search for laptop"
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
                        "xpath": "//button[@data-testid='search-button']",
                        "css_selector": "button[data-testid='search-button']",
                        "attributes": {
                            "data-testid": "search-button",
                            "type": "submit"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995202.6,
                "elapsed_time": 0.3,
                "description": "Click search button"
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
            },
            "metadata": {
                "step_start_time": 1640995202.9,
                "elapsed_time": 2.0,
                "description": "Wait for search results"
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
                        "xpath": "//div[@data-testid='product-card'][1]",
                        "css_selector": "div[data-testid='product-card']:first-child",
                        "attributes": {
                            "data-testid": "product-card",
                            "data-product-id": "laptop-123"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995204.9,
                "elapsed_time": 0.7,
                "description": "Click on first product"
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
                        "xpath": "//button[@data-testid='add-to-cart']",
                        "css_selector": "button[data-testid='add-to-cart']",
                        "attributes": {
                            "data-testid": "add-to-cart",
                            "class": "btn btn-primary"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995205.6,
                "elapsed_time": 0.5,
                "description": "Add product to cart"
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
                        "xpath": "//a[@data-testid='cart-link']",
                        "css_selector": "a[data-testid='cart-link']",
                        "attributes": {
                            "data-testid": "cart-link",
                            "href": "/cart"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995206.1,
                "elapsed_time": 0.4,
                "description": "Go to cart"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "success": True,
                            "text": "Shopping cart flow completed"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995206.5,
                "elapsed_time": 0.1,
                "description": "Mark shopping flow complete"
            }
        }
    ]


def get_form_submission_flow_steps() -> List[Dict[str, Any]]:
    """Generate steps for a complex form submission flow."""
    return [
        {
            "model_output": {
                "action": [
                    {
                        "go_to_url": {
                            "url": "https://forms.example.com/contact"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995200.0,
                "elapsed_time": 1.8,
                "description": "Navigate to contact form"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "John Doe",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@name='name']",
                        "css_selector": "input[name='name']",
                        "attributes": {
                            "name": "name",
                            "type": "text",
                            "required": True
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995201.8,
                "elapsed_time": 0.4,
                "description": "Enter name"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "john@example.com",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//input[@name='email']",
                        "css_selector": "input[name='email']",
                        "attributes": {
                            "name": "email",
                            "type": "email",
                            "required": True
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995202.2,
                "elapsed_time": 0.6,
                "description": "Enter email"
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
                        "xpath": "//select[@name='topic']",
                        "css_selector": "select[name='topic']",
                        "attributes": {
                            "name": "topic",
                            "required": True
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995202.8,
                "elapsed_time": 0.3,
                "description": "Open topic dropdown"
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
                        "xpath": "//option[@value='support']",
                        "css_selector": "option[value='support']",
                        "attributes": {
                            "value": "support"
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995203.1,
                "elapsed_time": 0.2,
                "description": "Select support topic"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "input_text": {
                            "text": "I need help with my account settings. The page seems to be loading slowly and I cannot access my profile information.",
                            "index": 0
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": [
                    {
                        "xpath": "//textarea[@name='message']",
                        "css_selector": "textarea[name='message']",
                        "attributes": {
                            "name": "message",
                            "rows": 5,
                            "required": True
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995203.3,
                "elapsed_time": 2.1,
                "description": "Enter message"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "scroll_down": {
                            "amount": 300
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995205.4,
                "elapsed_time": 0.3,
                "description": "Scroll to see submit button"
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
                        }
                    }
                ]
            },
            "metadata": {
                "step_start_time": 1640995205.7,
                "elapsed_time": 0.4,
                "description": "Submit form"
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
            },
            "metadata": {
                "step_start_time": 1640995206.1,
                "elapsed_time": 2.0,
                "description": "Wait for form submission"
            }
        },
        {
            "model_output": {
                "action": [
                    {
                        "done": {
                            "success": True,
                            "text": "Contact form submitted successfully"
                        }
                    }
                ]
            },
            "state": {
                "interacted_element": []
            },
            "metadata": {
                "step_start_time": 1640995208.1,
                "elapsed_time": 0.1,
                "description": "Form submission complete"
            }
        }
    ]


async def run_all_test_flows():
    """Run all example test flows and display results."""
    print("🧪 Running Browse-to-Test Incremental Flow Examples")
    print("=" * 70)
    
    # Configuration for Playwright tests
    playwright_config = Config(
        output=OutputConfig(
            framework="playwright",
            language="python",
            include_assertions=True,
            include_error_handling=True,
            include_logging=True,
            mask_sensitive_data=True,
            sensitive_data_keys=["username", "password"]
        ),
        processing=ProcessingConfig(
            analyze_actions_with_ai=False,  # Set to True if you have AI configured
            collect_system_context=False,
            strict_mode=False,
        ),
        verbose=True
    )
    
    # Configuration for Selenium tests
    selenium_config = Config(
        output=OutputConfig(
            framework="selenium",
            language="python",
            include_assertions=True,
            include_error_handling=True,
            include_logging=True,
            mask_sensitive_data=True,
            sensitive_data_keys=["username", "password"]
        ),
        processing=ProcessingConfig(
            analyze_actions_with_ai=False,
            collect_system_context=False,
            strict_mode=False,
        ),
        verbose=True
    )
    
    flows = [
        {
            "name": "Login Flow (Playwright)",
            "config": playwright_config,
            "steps": get_login_flow_steps(),
            "target_url": "https://example.com/login",
            "context_hints": {
                "flow_type": "authentication",
                "requires_authentication": True,
                "critical_elements": ["username", "password", "login-button"]
            }
        },
        {
            "name": "Shopping Cart Flow (Playwright)",
            "config": playwright_config,
            "steps": get_shopping_cart_flow_steps(),
            "target_url": "https://shop.example.com",
            "context_hints": {
                "flow_type": "e_commerce",
                "requires_search": True,
                "critical_elements": ["search-input", "add-to-cart", "cart-link"]
            }
        },
        {
            "name": "Form Submission (Selenium)",
            "config": selenium_config,
            "steps": get_form_submission_flow_steps(),
            "target_url": "https://forms.example.com/contact",
            "context_hints": {
                "flow_type": "form_submission",
                "has_validation": True,
                "critical_elements": ["name", "email", "message", "submit"]
            }
        }
    ]
    
    results = []
    
    for flow in flows:
        print(f"\n🎬 Running: {flow['name']}")
        
        runner = IncrementalTestFlowRunner(flow['config'])
        
        result = await runner.run_flow(
            flow_name=flow['name'],
            steps=flow['steps'],
            target_url=flow['target_url'],
            context_hints=flow['context_hints'],
            show_progress=True
        )
        
        results.append(result)
        
        # Save generated script to file
        script_filename = f"generated_{flow['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}.py"
        with open(script_filename, 'w') as f:
            f.write(result['final_script'])
        
        print(f"💾 Generated script saved to: {script_filename}")
        print("-" * 60)
    
    # Print summary
    print("\n📈 Overall Results Summary")
    print("=" * 40)
    
    total_flows = len(results)
    successful_flows = sum(1 for r in results if r['success'])
    total_steps = sum(r['total_steps_processed'] for r in results)
    successful_steps = sum(r['successful_steps'] for r in results)
    
    print(f"Total flows: {total_flows}")
    print(f"Successful flows: {successful_flows}")
    print(f"Total steps processed: {total_steps}")
    print(f"Successful steps: {successful_steps}")
    print(f"Success rate: {(successful_flows / total_flows * 100):.1f}%")
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"  {status} {result['flow_name']}: {result['successful_steps']}/{result['total_steps_processed']} steps")
    
    return results


def main():
    """Main entry point for running incremental test flows."""
    print("Starting incremental test flows...")
    results = asyncio.run(run_all_test_flows())
    
    # Save results summary
    summary_file = "incremental_flow_results.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📋 Detailed results saved to: {summary_file}")
    print("\n🎉 Incremental test flow demonstration complete!")


if __name__ == "__main__":
    main() 