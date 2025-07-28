#!/usr/bin/env python3
"""
Comprehensive NoneType Fix Test
Tests all the NoneType safety patterns implemented in the crawler
"""

import sys
import os
import logging
import time

# Add the current directory to the path so we can import the crawler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the safety functions from the main crawler
try:
    from enhanced_crawler_ui import safe_get, safe_nested_get, safe_ui_call, safe_ml_call, safe_items, validate_data_structure
    print("✅ Successfully imported safety functions")
except ImportError as e:
    print(f"❌ Failed to import safety functions: {e}")
    sys.exit(1)

def test_safe_get():
    """Test safe_get function with various inputs"""
    print("\n🔍 Testing safe_get function...")
    
    test_cases = [
        (None, 'title', 'default', "None object"),
        ({}, 'title', 'default', "Empty dict"),
        ({'title': 'test'}, 'title', 'default', "Valid dict"),
        ({'title': 'test'}, 'nonexistent', 'default', "Missing key"),
        ([], 'title', 'default', "List object"),
        ("string", 'title', 'default', "String object")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for obj, key, default, description in test_cases:
        try:
            result = safe_get(obj, key, default)
            print(f"  ✅ {description}: {result}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 safe_get: {passed}/{total} tests passed")
    return passed == total

def test_safe_nested_get():
    """Test safe_nested_get function with various inputs"""
    print("\n🔍 Testing safe_nested_get function...")
    
    test_cases = [
        (None, ['ml_classification', 'enhanced_classification', 'label'], 'default', "None object"),
        ({}, ['ml_classification', 'enhanced_classification', 'label'], 'default', "Empty dict"),
        ({'ml_classification': {}}, ['ml_classification', 'enhanced_classification', 'label'], 'default', "Partial dict"),
        ({'ml_classification': {'enhanced_classification': {'label': 'test'}}}, ['ml_classification', 'enhanced_classification', 'label'], 'default', "Valid nested dict"),
        ({'ml_classification': {'enhanced_classification': {}}}, ['ml_classification', 'enhanced_classification', 'label'], 'default', "Missing nested key"),
        ([], ['ml_classification', 'enhanced_classification', 'label'], 'default', "List object")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for obj, keys, default, description in test_cases:
        try:
            result = safe_nested_get(obj, keys, default)
            print(f"  ✅ {description}: {result}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 safe_nested_get: {passed}/{total} tests passed")
    return passed == total

def test_safe_items():
    """Test safe_items function with various inputs"""
    print("\n🔍 Testing safe_items function...")
    
    test_cases = [
        (None, "None object"),
        ({}, "Empty dict"),
        ({'title': 'test', 'description': 'test'}, "Valid dict"),
        ([], "List object"),
        ("string", "String object")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for obj, description in test_cases:
        try:
            result = safe_items(obj)
            print(f"  ✅ {description}: {len(result)} items")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 safe_items: {passed}/{total} tests passed")
    return passed == total

def test_safe_ui_call():
    """Test safe_ui_call function with mock UI components"""
    print("\n🔍 Testing safe_ui_call function...")
    
    # Mock UI component
    class MockUIComponent:
        def __init__(self, value):
            self.value = value
        
        def isChecked(self):
            return self.value
    
    test_cases = [
        (None, 'isChecked', "None component"),
        (MockUIComponent(True), 'isChecked', "Valid component - True"),
        (MockUIComponent(False), 'isChecked', "Valid component - False"),
        (MockUIComponent(True), 'nonexistent', "Invalid method"),
        ("string", 'isChecked', "String object")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for component, method, description in test_cases:
        try:
            result = safe_ui_call(component, method)
            print(f"  ✅ {description}: {result}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 safe_ui_call: {passed}/{total} tests passed")
    return passed == total

def test_safe_ml_call():
    """Test safe_ml_call function with mock ML models"""
    print("\n🔍 Testing safe_ml_call function...")
    
    # Mock ML model
    class MockMLModel:
        def __init__(self, should_fail=False):
            self.should_fail = should_fail
        
        def __call__(self, text, **kwargs):
            if self.should_fail:
                raise Exception("ML model error")
            return [{'label': 'test', 'score': 0.8}]
    
    test_cases = [
        (None, "text", "None model"),
        (MockMLModel(False), "text", "Valid model"),
        (MockMLModel(True), "text", "Failing model"),
        ("string", "text", "String object")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for model, text, description in test_cases:
        try:
            result = safe_ml_call(model, text)
            print(f"  ✅ {description}: {result}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 safe_ml_call: {passed}/{total} tests passed")
    return passed == total

def test_validate_data_structure():
    """Test validate_data_structure function with various inputs"""
    print("\n🔍 Testing validate_data_structure function...")
    
    test_cases = [
        (None, "None data"),
        ({}, "Empty dict"),
        ({'title': 'test', 'description': 'test', 'tags': ['tag1']}, "Valid data"),
        ({'title': 'test', 'tags': 'not_a_list'}, "Invalid tags type"),
        ([], "List object"),
        ("string", "String object")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for data, description in test_cases:
        try:
            result = validate_data_structure(data)
            print(f"  ✅ {description}: {result['title'][:20]}...")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 validate_data_structure: {passed}/{total} tests passed")
    return passed == total

def test_critical_none_scenarios():
    """Test critical None scenarios that were causing crashes"""
    print("\n🔍 Testing critical None scenarios...")
    
    scenarios = [
        ("result.items() on None", lambda: safe_items(None)),
        ("result.get() on None", lambda: safe_get(None, 'title', 'default')),
        ("nested get on None", lambda: safe_nested_get(None, ['ml_classification', 'label'], 'default')),
        ("UI call on None", lambda: safe_ui_call(None, 'isChecked')),
        ("ML call on None", lambda: safe_ml_call(None, "text")),
        ("validate None data", lambda: validate_data_structure(None))
    ]
    
    passed = 0
    total = len(scenarios)
    
    for description, test_func in scenarios:
        try:
            result = test_func()
            print(f"  ✅ {description}: {result}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {description}: {e}")
    
    print(f"  📊 Critical scenarios: {passed}/{total} tests passed")
    return passed == total

def main():
    """Run all NoneType safety tests"""
    print("🚀 Starting Comprehensive NoneType Fix Test")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        test_safe_get,
        test_safe_nested_get,
        test_safe_items,
        test_safe_ui_call,
        test_safe_ml_call,
        test_validate_data_structure,
        test_critical_none_scenarios
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    print(f"⏱️ Duration: {duration:.2f} seconds")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! NoneType fixes are working correctly.")
        print("✅ The crawler should now be protected against NoneType errors.")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Some NoneType issues may remain.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 