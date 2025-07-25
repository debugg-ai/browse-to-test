#!/usr/bin/env python3

"""
Script to check what files would be included in the package distribution.
"""

import os
from pathlib import Path
from setuptools import find_packages
import glob

def find_package_files():
    """Find all files that should be included in the package."""
    print("🔍 Checking package files that should be included...")
    print("=" * 60)
    
    # Check Python packages
    packages = find_packages()
    print(f"📦 Found {len(packages)} Python packages:")
    for pkg in packages:
        print(f"  - {pkg}")
    
    print("\n📁 Checking non-Python files that should be included:")
    
    # Check JSON files in common
    common_json = list(Path("browse_to_test/output_langs/common").glob("*.json"))
    print(f"\n🔧 Common JSON files ({len(common_json)}):")
    for file in common_json:
        print(f"  - {file}")
        if not file.exists():
            print(f"    ❌ FILE MISSING!")
    
    # Check metadata files
    metadata_files = list(Path("browse_to_test/output_langs").glob("*/metadata.json"))
    print(f"\n📋 Metadata files ({len(metadata_files)}):")
    for file in metadata_files:
        print(f"  - {file}")
        if not file.exists():
            print(f"    ❌ FILE MISSING!")
    
    # Check template files
    template_files = list(Path("browse_to_test/output_langs").glob("*/templates/*.txt"))
    print(f"\n📝 Template files ({len(template_files)}):")
    for file in template_files:
        print(f"  - {file}")
        if not file.exists():
            print(f"    ❌ FILE MISSING!")
    
    # Check if files exist
    critical_files = [
        "browse_to_test/output_langs/common/constants.json",
        "browse_to_test/output_langs/common/messages.json", 
        "browse_to_test/output_langs/common/patterns.json",
        "browse_to_test/output_langs/typescript/metadata.json",
        "browse_to_test/output_langs/typescript/templates/base_imports.txt",
        "browse_to_test/output_langs/typescript/templates/exception_classes.txt",
        "browse_to_test/output_langs/typescript/templates/utility_functions.txt",
        "browse_to_test/output_langs/python/metadata.json",
        "browse_to_test/output_langs/python/templates/base_imports.txt",
        "browse_to_test/output_langs/python/templates/exception_classes.txt",
        "browse_to_test/output_langs/python/templates/utility_functions.txt",
    ]
    
    print(f"\n🎯 Critical files check ({len(critical_files)}):")
    missing_files = []
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING!")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  WARNING: {len(missing_files)} critical files are missing!")
        return False
    else:
        print(f"\n🎉 SUCCESS: All critical files are present!")
        return True

def test_package_data_patterns():
    """Test the package_data patterns from setup.py."""
    print("\n" + "=" * 60)
    print("🧪 Testing package_data patterns...")
    
    patterns = [
        "browse_to_test/output_langs/common/*.json",
        "browse_to_test/output_langs/*/metadata.json",
        "browse_to_test/output_langs/*/templates/*.txt",
    ]
    
    for pattern in patterns:
        matches = glob.glob(pattern)
        print(f"\nPattern: {pattern}")
        print(f"Matches ({len(matches)}):")
        for match in matches:
            print(f"  - {match}")
        
        if not matches:
            print(f"  ❌ No matches found for pattern!")

if __name__ == "__main__":
    print("📦 Package File Checker")
    
    files_ok = find_package_files()
    test_package_data_patterns()
    
    if files_ok:
        print("\n✅ Package should build correctly with all files included!")
    else:
        print("\n❌ Package may be missing critical files!") 