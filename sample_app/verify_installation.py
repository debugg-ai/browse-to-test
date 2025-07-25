#!/usr/bin/env python3
"""
Quick Browse-to-Test Installation Verification

This script performs a quick check to verify that the browse-to-test library
is installed correctly and can be imported.

Usage:
    python verify_installation.py
"""

import sys
import subprocess
import pkg_resources

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    min_version = (3, 8)
    
    if version >= min_version:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} (>= {min_version[0]}.{min_version[1]})")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires >= {min_version[0]}.{min_version[1]})")
        return False

def check_package_installed(package_name):
    """Check if a package is installed."""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def check_import(module_name):
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        return True
    except ImportError:
        return False

def suggest_installation():
    """Suggest installation commands."""
    print("\n📦 Installation suggestions:")
    print("   pip install browse-to-test[all]")
    print("   # Or specific components:")
    print("   pip install browse-to-test[openai,playwright]")
    print("   pip install browse-to-test[anthropic,selenium]")

def main():
    print("🔍 Browse-to-Test Installation Verification")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check Python version
    print("\n1️⃣ Python Version Check:")
    if not check_python_version():
        all_checks_passed = False
    
    # Check core package
    print("\n2️⃣ Core Package Check:")
    if check_package_installed("browse-to-test"):
        print("✅ browse-to-test package is installed")
        
        # Get version if possible
        try:
            version = pkg_resources.get_distribution("browse-to-test").version
            print(f"   📌 Version: {version}")
        except:
            print("   ⚠️  Could not determine version")
    else:
        print("❌ browse-to-test package is NOT installed")
        all_checks_passed = False
    
    # Check imports
    print("\n3️⃣ Import Check:")
    if check_import("browse_to_test"):
        print("✅ browse_to_test module imports successfully")
        
        # Try to import specific components
        components = [
            ("browse_to_test.convert", "Main convert function"),
            ("browse_to_test.ConfigBuilder", "ConfigBuilder class"),
            ("browse_to_test.E2eTestConverter", "E2eTestConverter class"),
            ("browse_to_test.IncrementalSession", "IncrementalSession class"),
        ]
        
        for component, description in components:
            try:
                module_path, attr = component.rsplit('.', 1)
                module = __import__(module_path, fromlist=[attr])
                getattr(module, attr)
                print(f"   ✅ {description}")
            except (ImportError, AttributeError):
                print(f"   ❌ {description}")
                all_checks_passed = False
    else:
        print("❌ browse_to_test module cannot be imported")
        all_checks_passed = False
    
    # Check optional dependencies
    print("\n4️⃣ Optional Dependencies Check:")
    optional_deps = [
        ("openai", "OpenAI provider"),
        ("anthropic", "Anthropic provider"),
        ("playwright", "Playwright framework"),
        ("selenium", "Selenium framework"),
    ]
    
    for package, description in optional_deps:
        if check_package_installed(package):
            print(f"   ✅ {description} ({package})")
        else:
            print(f"   ⚠️  {description} ({package}) - optional")
    
    # Environment variables check
    print("\n5️⃣ Environment Variables Check:")
    import os
    
    api_keys = [
        ("OPENAI_API_KEY", "OpenAI API access"),
        ("ANTHROPIC_API_KEY", "Anthropic API access"),
    ]
    
    for env_var, description in api_keys:
        if os.getenv(env_var):
            print(f"   ✅ {env_var} is set")
        else:
            print(f"   ⚠️  {env_var} not set - {description} will not work")
    
    # Final result
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 Installation verification PASSED!")
        print("   You can now run the sample app:")
        print("   python main.py")
        print("   python simple_demo.py")
        return 0
    else:
        print("❌ Installation verification FAILED!")
        suggest_installation()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 