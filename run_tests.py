#!/usr/bin/env python3
"""
Test runner script for the Flask-RESTful School Management System
"""

import sys
import subprocess
import os

def run_tests():
    """Run the test suite"""
    print("🧪 Running Login Class Tests...")
    print("=" * 50)
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_login.py", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], check=True, capture_output=False)
        
        print("\n✅ All tests passed!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n❌ pytest not found. Please install it with: pip install pytest")
        return False

def install_pytest():
    """Install pytest if not available"""
    try:
        import pytest
        return True
    except ImportError:
        print("📦 Installing pytest...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest"], check=True)
        return True

if __name__ == "__main__":
    print("🚀 Flask-RESTful School Management System - Test Runner")
    print("=" * 60)
    
    # Install pytest if needed
    if not install_pytest():
        sys.exit(1)
    
    # Run tests
    success = run_tests()
    sys.exit(0 if success else 1)

