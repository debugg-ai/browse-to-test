#!/usr/bin/env python3
"""
Parallel test runner script for browse-to-test library.

This script runs the full test suite in parallel and provides a summary.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_parallel_tests():
    """Run the test suite in parallel and provide a summary."""
    print("🚀 Running browse-to-test test suite in parallel...")
    print("=" * 60)
    
    start_time = time.time()
    
    # Run tests with parallel execution
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/", 
        "-v", 
        "--tb=short",
        "--durations=10"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Print results
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print("=" * 60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            print("\n📊 Test Summary:")
            
            # Extract test count from output
            lines = result.stdout.split('\n')
            for line in lines:
                if 'passed' in line and ('failed' in line or 'error' in line or 'skipped' in line):
                    print(f"   {line.strip()}")
                elif line.startswith('=') and ('passed' in line or 'failed' in line):
                    print(f"   {line.strip()}")
                    
            # Show parallel execution info
            for line in lines:
                if 'workers' in line or 'created:' in line:
                    print(f"   🔧 {line.strip()}")
                    break
                    
        else:
            print("❌ Some tests failed!")
            print("\n🔍 Failure Summary:")
            print(result.stdout)
            print("\n🐛 Error Details:")
            print(result.stderr)
            
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out after 10 minutes")
        return 1
    except Exception as e:
        print(f"💥 Error running tests: {e}")
        return 1


def main():
    """Main entry point."""
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    if not (project_root / "tests").exists():
        print("❌ Tests directory not found. Make sure you're in the project root.")
        return 1
    
    # Run tests
    return run_parallel_tests()


if __name__ == "__main__":
    sys.exit(main())