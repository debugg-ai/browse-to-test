#!/usr/bin/env python3
"""
Demo script showcasing the new robust comment management system.

This script demonstrates how the CommentManager automatically generates
language-appropriate comments for different programming languages.
"""

from browse_to_test.core.configuration import CommentManager


def demonstrate_comment_system():
    """Demonstrate the comment system across all supported languages."""
    
    print("🔧 Browse-to-Test Comment Management System Demo")
    print("=" * 60)
    print()
    
    # Sample data for demonstration
    step_data = {
        "description": "Fill login form with user credentials",
        "action_type": "fill", 
        "selector": "#username",
        "value": "testuser@example.com",
        "timeout": 5000
    }
    
    context_data = {
        "url": "https://app.example.com/login",
        "page_title": "Login - Example App",
        "element_count": 12,
        "viewport": "1366x768",
        "browser": "Chrome"
    }
    
    supported_languages = ["python", "javascript", "typescript", "csharp", "java"]
    
    for language in supported_languages:
        print(f"📝 {language.upper()} COMMENTS")
        print("-" * 40)
        
        manager = CommentManager(language)
        
        # 1. Step header with metadata
        print("Step Header:")
        step_header = manager.step_header(
            step_number=1,
            description=step_data["description"],
            metadata=step_data,
            indent="    "
        )
        for line in step_header:
            print(f"  {line}")
        print()
        
        # 2. Contextual information
        print("Context Information:")
        context_lines = manager.contextual_info_comment(context_data, "    ")
        for line in context_lines:
            print(f"  {line}")
        print()
        
        # 3. Action comment
        print("Action Comment:")
        action_comment = manager.action_comment(
            step_data["action_type"],
            step_data["selector"],
            {"value": step_data["value"], "timeout": f"{step_data['timeout']}ms"},
            "    "
        )
        print(f"  {action_comment}")
        print()
        
        # 4. Error comment
        print("Error Comment:")
        error_comment = manager.error_comment(
            "Element not found", 
            "Selector #username was not found on page",
            "    "
        )
        print(f"  {error_comment}")
        print()
        
        # 5. Section separator
        print("Section Separator:")
        separator_lines = manager.section_separator("TEST EXECUTION", "    ", 50)
        for line in separator_lines:
            print(f"  {line}")
        print()
        
        # 6. Documentation string
        print("Documentation String:")
        doc_lines = manager.doc_string(
            "Automated login test function",
            {"username": "The username to login with", "password": "The password to use"},
            "Boolean indicating if login was successful",
            "    "
        )
        for line in doc_lines:
            print(f"  {line}")
        print()
        
        print("=" * 60)
        print()


def demonstrate_old_vs_new():
    """Show the difference between old hardcoded comments and new system."""
    
    print("🔄 OLD vs NEW Comment System Comparison")
    print("=" * 60)
    print()
    
    step_description = "Click the submit button"
    
    languages = ["python", "javascript", "typescript", "java"]
    
    for language in languages:
        print(f"Language: {language.upper()}")
        print("-" * 30)
        
        # Old way (hardcoded Python-style)
        print("❌ OLD (hardcoded):")
        print(f"    # Step 1: {step_description}")
        print(f"    # Error: Something went wrong")
        print()
        
        # New way (language-aware)
        print("✅ NEW (language-aware):")
        manager = CommentManager(language)
        step_comment = manager.step_header(1, step_description, indent="    ")
        error_comment = manager.error_comment("Something went wrong", indent="    ")
        
        for line in step_comment:
            print(f"    {line}")
        print(f"    {error_comment}")
        print()
        print("-" * 30)
        print()


def demonstrate_detailed_contextual_comments():
    """Show how detailed contextual comments work."""
    
    print("📋 Detailed Contextual Comments Demo")
    print("=" * 60)
    print()
    
    # Simulate a complex automation scenario
    scenario = {
        "page_info": {
            "url": "https://ecommerce.example.com/checkout",
            "page_title": "Checkout - Example Store",
            "element_count": 28,
            "viewport": "1920x1080",
            "browser": "Chrome",
            "user_inputs": ["email", "address", "credit_card", "cvv"]
        },
        "steps": [
            {
                "description": "Navigate to checkout page",
                "action_type": "navigate",
                "url": "https://ecommerce.example.com/checkout",
                "wait_for": "page_load"
            },
            {
                "description": "Fill shipping address form",
                "action_type": "fill",
                "selector": "#shipping-address",
                "value": "123 Main St, Anytown, USA",
                "validation": "required"
            },
            {
                "description": "Select payment method",
                "action_type": "click",
                "selector": "#payment-credit-card",
                "wait_for": "element_visible"
            }
        ]
    }
    
    manager = CommentManager("typescript")  # Example with TypeScript
    
    print("TypeScript Example - E-commerce Checkout Flow:")
    print()
    
    # Page context
    print("Page Context:")
    context_lines = manager.contextual_info_comment(scenario["page_info"], "  ")
    for line in context_lines:
        print(line)
    print()
    
    # Step-by-step with detailed comments
    for i, step in enumerate(scenario["steps"], 1):
        step_lines = manager.step_header(
            step_number=i,
            description=step["description"],
            metadata=step,
            indent="  "
        )
        
        print(f"Step {i}:")
        for line in step_lines:
            print(line)
        
        # Additional action details
        action_details = {
            "selector": step.get("selector"),
            "value": step.get("value"),
            "timeout": step.get("timeout", "default"),
            "validation": step.get("validation"),
            "wait_for": step.get("wait_for")
        }
        action_details = {k: v for k, v in action_details.items() if v}  # Remove None values
        
        if action_details:
            action_comment = manager.action_comment(
                step["action_type"],
                step.get("selector", step.get("url", "")),
                action_details,
                "  "
            )
            print(action_comment)
        print()


if __name__ == "__main__":
    demonstrate_comment_system()
    demonstrate_old_vs_new()
    demonstrate_detailed_contextual_comments()
    
    print("🎉 Comment Management System Demo Complete!")
    print()
    print("Key Benefits:")
    print("✅ Language-specific comment formats")
    print("✅ Detailed contextual information")
    print("✅ Consistent formatting across generators")
    print("✅ Metadata-rich step documentation")
    print("✅ Error comments with proper formatting")
    print("✅ Centralized comment management") 