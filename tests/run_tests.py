#!/usr/bin/env python3
"""
Test runner for BookClubBot
Run this file to execute all tests
"""
import unittest
import sys
import os

# Add the parent directory to the path so imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load all tests
loader = unittest.TestLoader()
suite = loader.discover(start_dir=os.path.dirname(__file__), pattern='test_*.py')

# Run the tests
runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)

# Exit with appropriate code
sys.exit(not result.wasSuccessful())