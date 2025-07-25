#!/usr/bin/env python3

"""
Pre-commit Check Script

Quick validation script to run before commits to ensure package integrity.
This is a lightweight version of the full validation that can be run quickly.
"""

import sys
import json
from pathlib import Path
from typing import List

class Colors:
    """ANSI color codes for terminal output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

class PreCommitChecker:
    """Quick pre-commit validation checks."""
    
    def __init__(self, project_root: Path = None):
        """Initialize the checker."""
        self.project_root = project_root or Path.cwd()
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check_critical_files(self) -> bool:
        """Check that critical files exist."""
        print_info("Checking critical files...")
        
        critical_files = [
            "browse_to_test/output_langs/common/constants.json",
            "browse_to_test/output_langs/common/messages.json", 
            "browse_to_test/output_langs/common/patterns.json",
            "browse_to_test/output_langs/typescript/metadata.json",
            "browse_to_test/output_langs/python/metadata.json",
            "setup.py",
            "MANIFEST.in",
            "README.md",
        ]
        
        missing = []
        for file_path in critical_files:
            if not (self.project_root / file_path).exists():
                missing.append(file_path)
        
        if missing:
            for file_path in missing:
                print_error(f"Missing: {file_path}")
            self.errors.extend([f"Missing file: {f}" for f in missing])
            return False
        
        print_success(f"All {len(critical_files)} critical files present")
        return True
    
    def check_json_syntax(self) -> bool:
        """Check JSON files for syntax errors."""
        print_info("Checking JSON syntax...")
        
        json_files = list(self.project_root.glob("browse_to_test/output_langs/**/*.json"))
        invalid = []
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                print_error(f"Invalid JSON: {json_file.relative_to(self.project_root)} - {e}")
                invalid.append(str(json_file.relative_to(self.project_root)))
        
        if invalid:
            self.errors.extend([f"Invalid JSON: {f}" for f in invalid])
            return False
        
        print_success(f"All {len(json_files)} JSON files are valid")
        return True
    
    def check_package_config(self) -> bool:
        """Check package configuration files."""
        print_info("Checking package configuration...")
        
        # Check setup.py
        setup_py = self.project_root / "setup.py"
        if setup_py.exists():
            setup_content = setup_py.read_text()
            required_configs = [
                "include_package_data=True",
                "package_data=",
                "*.json",
                "*.txt"
            ]
            
            missing_configs = []
            for config in required_configs:
                if config not in setup_content:
                    missing_configs.append(config)
            
            if missing_configs:
                for config in missing_configs:
                    print_warning(f"setup.py missing: {config}")
                self.warnings.extend([f"setup.py missing: {c}" for c in missing_configs])
        
        # Check MANIFEST.in
        manifest_file = self.project_root / "MANIFEST.in"
        if manifest_file.exists():
            manifest_content = manifest_file.read_text()
            required_patterns = [
                "*.json",
                "*.txt"
            ]
            
            for pattern in required_patterns:
                if pattern not in manifest_content:
                    print_warning(f"MANIFEST.in missing pattern: {pattern}")
                    self.warnings.append(f"MANIFEST.in missing pattern: {pattern}")
        
        print_success("Package configuration checked")
        return True
    
    def check_version_consistency(self) -> bool:
        """Check that version is consistent across files."""
        print_info("Checking version consistency...")
        
        # Get version from __init__.py
        init_file = self.project_root / "browse_to_test" / "__init__.py"
        if not init_file.exists():
            print_error("__init__.py not found")
            self.errors.append("__init__.py not found")
            return False
        
        init_content = init_file.read_text()
        version = None
        for line in init_content.splitlines():
            if line.startswith("__version__"):
                version = line.split('"')[1]
                break
        
        if not version:
            print_warning("Version not found in __init__.py")
            self.warnings.append("Version not found in __init__.py")
            return True
        
        print_success(f"Version found: {version}")
        return True
    
    def run_checks(self) -> bool:
        """Run all pre-commit checks."""
        print(f"{Colors.BOLD}🔍 Running pre-commit checks...{Colors.END}")
        
        checks = [
            ("Critical Files", self.check_critical_files),
            ("JSON Syntax", self.check_json_syntax),
            ("Package Config", self.check_package_config),
            ("Version Consistency", self.check_version_consistency),
        ]
        
        results = {}
        for name, check_func in checks:
            try:
                results[name] = check_func()
            except Exception as e:
                print_error(f"Check '{name}' failed: {e}")
                results[name] = False
                self.errors.append(f"Check '{name}' failed: {e}")
        
        # Summary
        print(f"\n{Colors.BOLD}Pre-commit Check Summary:{Colors.END}")
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for name, result in results.items():
            status = "✅" if result else "❌"
            print(f"  {status} {name}")
        
        if self.warnings:
            print_warning(f"\n{len(self.warnings)} warnings:")
            for warning in self.warnings:
                print_warning(f"  - {warning}")
        
        if self.errors:
            print_error(f"\n{len(self.errors)} errors:")
            for error in self.errors:
                print_error(f"  - {error}")
            
            print_error("🚫 Pre-commit checks failed!")
            return False
        
        if passed == total:
            print_success("🎉 All pre-commit checks passed!")
            return True
        else:
            print_error("🚫 Some pre-commit checks failed!")
            return False

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pre-commit checks for browse-to-test")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    
    args = parser.parse_args()
    
    checker = PreCommitChecker(args.project_root)
    success = checker.run_checks()
    
    if not success:
        print_error("\n💡 Fix the issues above before committing.")
        print_error("   For full validation, run: python scripts/validate_package.py")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 