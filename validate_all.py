#!/usr/bin/env python3

"""
Master Validation Script

Runs all package validation checks in the correct order.
This is the one-stop script for complete package validation.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str, color: str = Colors.CYAN):
    """Print a formatted header."""
    print(f"\n{color}{Colors.BOLD}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Colors.END}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def run_script(script_path: Path, args: List[str] = None) -> Tuple[bool, str]:
    """Run a validation script and return success status and output."""
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        output = result.stdout
        if result.stderr:
            output += f"\nStderr:\n{result.stderr}"
        
        return result.returncode == 0, output
        
    except Exception as e:
        return False, f"Failed to run script: {e}"

def main():
    """Run all validation scripts."""
    print_header("🚀 Complete Package Validation", Colors.MAGENTA)
    print_info("Running all validation checks...")
    
    project_root = Path.cwd()
    scripts_dir = project_root / "scripts"
    
    # Define validation steps
    validations = [
        {
            "name": "Pre-commit Checks",
                         "script": scripts_dir / "pre_commit_check.py",
            "description": "Quick validation of critical files and JSON syntax",
            "args": [],
            "required": True
        },
        {
            "name": "Full Package Validation", 
            "script": scripts_dir / "validate_package.py",
            "description": "Comprehensive package validation including build test",
            "args": [],
            "required": True
        },
        {
            "name": "Built Package Testing",
            "script": scripts_dir / "test_built_package.py", 
            "description": "Test package installation and functionality in clean environment",
            "args": [],
            "required": True
        }
    ]
    
    results = {}
    failed_validations = []
    
    for validation in validations:
        print_header(f"🔍 {validation['name']}")
        print_info(validation['description'])
        
        if not validation['script'].exists():
            print_error(f"Script not found: {validation['script']}")
            results[validation['name']] = False
            if validation['required']:
                failed_validations.append(validation['name'])
            continue
        
        success, output = run_script(validation['script'], validation.get('args', []))
        results[validation['name']] = success
        
        if success:
            print_success(f"{validation['name']} passed!")
        else:
            print_error(f"{validation['name']} failed!")
            if validation['required']:
                failed_validations.append(validation['name'])
        
        # Show output if requested or if failed
        if not success or '--verbose' in sys.argv:
            print(f"\n{Colors.YELLOW}Output:{Colors.END}")
            print(output)
    
    # Final summary
    print_header("📊 Validation Summary", Colors.MAGENTA)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"{Colors.BOLD}Results: {passed}/{total} validations passed{Colors.END}")
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    if failed_validations:
        print_error(f"\n{len(failed_validations)} critical validations failed:")
        for validation in failed_validations:
            print_error(f"  - {validation}")
        
        print_error("\n🚫 Package validation failed!")
        print_error("   Fix the issues above before pushing to GitHub.")
        return False
    
    elif passed < total:
        print_info(f"\n{total - passed} non-critical validations failed.")
        print_info("Package may still be usable, but consider fixing these issues.")
    
    print_success("\n🎉 All critical validations passed!")
    print_success("   Package is ready for release!")
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all package validations")
    parser.add_argument("--verbose", action="store_true", help="Show output from all validations")
    
    args = parser.parse_args()
    
    success = main()
    sys.exit(0 if success else 1) 