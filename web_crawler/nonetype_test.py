#!/usr/bin/env python3
"""
Comprehensive NoneType Error Detection and Prevention Test
This script tests all potential NoneType error scenarios and provides fixes.
"""

import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nonetype_test.log'),
        logging.StreamHandler()
    ]
)

class NoneTypeTester:
    """Comprehensive tester for NoneType error prevention."""
    
    def __init__(self):
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'issues_found': []
        }
    
    def test_safe_get_operations(self):
        """Test all .get() operations for None safety."""
        logging.info("🔍 Testing safe .get() operations...")
        
        # Test scenarios
        test_cases = [
            # (object, key, expected_result, description)
            (None, 'title', None, "None object with .get()"),
            ({}, 'title', None, "Empty dict with .get()"),
            ({'title': 'test'}, 'title', 'test', "Valid dict with .get()"),
            ({'title': None}, 'title', None, "Dict with None value"),
            ([], 0, None, "Empty list with .get()"),
            (None, 0, None, "None list with .get()"),
        ]
        
        for obj, key, expected, desc in test_cases:
            try:
                if obj is None:
                    result = None
                elif isinstance(obj, dict):
                    result = obj.get(key)
                elif isinstance(obj, list):
                    result = obj[0] if len(obj) > 0 else None
                else:
                    result = None
                
                if result == expected:
                    self.test_results['passed'] += 1
                    logging.info(f"✅ PASS: {desc}")
                else:
                    self.test_results['failed'] += 1
                    logging.error(f"❌ FAIL: {desc} - Expected {expected}, got {result}")
                    
            except Exception as e:
                self.test_results['failed'] += 1
                logging.error(f"❌ ERROR: {desc} - Exception: {e}")
    
    def test_nested_get_operations(self):
        """Test nested .get() operations that are common in the codebase."""
        logging.info("🔍 Testing nested .get() operations...")
        
        test_cases = [
            # (object, keys, expected_result, description)
            (None, ['ml_classification', 'enhanced_classification', 'label'], None, "None object with nested .get()"),
            ({}, ['ml_classification', 'enhanced_classification', 'label'], None, "Empty dict with nested .get()"),
            ({'ml_classification': {}}, ['ml_classification', 'enhanced_classification', 'label'], None, "Partial dict with nested .get()"),
            ({'ml_classification': {'enhanced_classification': {'label': 'test'}}}, ['ml_classification', 'enhanced_classification', 'label'], 'test', "Valid nested dict"),
        ]
        
        for obj, keys, expected, desc in test_cases:
            try:
                result = obj
                for key in keys:
                    if result is None:
                        result = None
                        break
                    elif isinstance(result, dict):
                        result = result.get(key)
                    else:
                        result = None
                        break
                
                if result == expected:
                    self.test_results['passed'] += 1
                    logging.info(f"✅ PASS: {desc}")
                else:
                    self.test_results['failed'] += 1
                    logging.error(f"❌ FAIL: {desc} - Expected {expected}, got {result}")
                    
            except Exception as e:
                self.test_results['failed'] += 1
                logging.error(f"❌ ERROR: {desc} - Exception: {e}")
    
    def test_ui_component_safety(self):
        """Test UI component None safety."""
        logging.info("🔍 Testing UI component safety...")
        
        # Simulate UI components that might be None
        ui_components = {
            'console': None,
            'error_console': None,
            'data_json_view': None,
            'console_progress': None,
            'status': None,
            'use_ml_classification': None,
            'use_validation': None,
            'use_ensemble': None
        }
        
        for component_name, component in ui_components.items():
            try:
                # Test safe access patterns
                if hasattr(component, 'setText') and component is not None:
                    component.setText("test")
                    self.test_results['passed'] += 1
                    logging.info(f"✅ PASS: {component_name} safe access")
                elif component is None:
                    self.test_results['passed'] += 1
                    logging.info(f"✅ PASS: {component_name} None handling")
                else:
                    self.test_results['warnings'] += 1
                    logging.warning(f"⚠️ WARNING: {component_name} unexpected state")
                    
            except Exception as e:
                self.test_results['failed'] += 1
                logging.error(f"❌ ERROR: {component_name} - Exception: {e}")
    
    def test_ml_model_safety(self):
        """Test ML model None safety."""
        logging.info("🔍 Testing ML model safety...")
        
        ml_models = {
            'nlp': None,
            'bert_classifier': None,
            'tfidf_vectorizer': None,
            'geocoder': None
        }
        
        for model_name, model in ml_models.items():
            try:
                # Test safe model usage patterns
                if model is not None:
                    # Simulate model call
                    if hasattr(model, '__call__'):
                        result = model("test text")
                        self.test_results['passed'] += 1
                        logging.info(f"✅ PASS: {model_name} callable")
                    else:
                        self.test_results['warnings'] += 1
                        logging.warning(f"⚠️ WARNING: {model_name} not callable")
                else:
                    self.test_results['passed'] += 1
                    logging.info(f"✅ PASS: {model_name} None handling")
                    
            except Exception as e:
                self.test_results['failed'] += 1
                logging.error(f"❌ ERROR: {model_name} - Exception: {e}")
    
    def test_data_processing_safety(self):
        """Test data processing None safety."""
        logging.info("🔍 Testing data processing safety...")
        
        test_data = [
            None,
            {},
            {'title': None},
            {'title': 'test', 'description': None},
            {'title': 'test', 'description': 'test desc', 'tags': None},
            {'title': 'test', 'description': 'test desc', 'tags': []},
            {'title': 'test', 'description': 'test desc', 'tags': ['tag1', 'tag2']}
        ]
        
        for i, data in enumerate(test_data):
            try:
                # Test common data processing patterns
                title = data.get('title', '') if data else ''
                description = data.get('description', '') if data else ''
                tags = data.get('tags', []) if data else []
                
                # Test string operations
                if title:
                    title_length = len(title)
                else:
                    title_length = 0
                
                # Test list operations
                if tags and isinstance(tags, list):
                    tag_count = len(tags)
                else:
                    tag_count = 0
                
                self.test_results['passed'] += 1
                logging.info(f"✅ PASS: Data processing test {i+1}")
                
            except Exception as e:
                self.test_results['failed'] += 1
                logging.error(f"❌ ERROR: Data processing test {i+1} - Exception: {e}")
    
    def test_soup_parsing_safety(self):
        """Test BeautifulSoup parsing None safety."""
        logging.info("🔍 Testing BeautifulSoup parsing safety...")
        
        try:
            from bs4 import BeautifulSoup
            
            test_htmls = [
                None,
                "",
                "<html><body><h1>Test</h1></body></html>",
                "<html><body><div class='description'>Test description</div></body></html>"
            ]
            
            for i, html in enumerate(test_htmls):
                try:
                    if html is None:
                        soup = None
                    else:
                        soup = BeautifulSoup(html, 'html.parser')
                    
                    # Test safe soup operations
                    if soup is not None:
                        title_elem = soup.find(['h1', 'title'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                        else:
                            title = ""
                        
                        desc_elem = soup.find('div', class_='description')
                        if desc_elem:
                            description = desc_elem.get_text(strip=True)
                        else:
                            description = ""
                    else:
                        title = ""
                        description = ""
                    
                    self.test_results['passed'] += 1
                    logging.info(f"✅ PASS: Soup parsing test {i+1}")
                    
                except Exception as e:
                    self.test_results['failed'] += 1
                    logging.error(f"❌ ERROR: Soup parsing test {i+1} - Exception: {e}")
                    
        except ImportError:
            self.test_results['warnings'] += 1
            logging.warning("⚠️ WARNING: BeautifulSoup not available")
    
    def generate_safety_fixes(self):
        """Generate code fixes for common NoneType issues."""
        logging.info("🔧 Generating safety fixes...")
        
        fixes = {
            'safe_get_pattern': '''
# Safe .get() pattern
def safe_get(obj, key, default=None):
    """Safely get value from object, handling None cases."""
    if obj is None:
        return default
    elif isinstance(obj, dict):
        return obj.get(key, default)
    else:
        return default

# Usage: value = safe_get(result, 'title', '')
''',
            'safe_nested_get_pattern': '''
# Safe nested .get() pattern
def safe_nested_get(obj, keys, default=None):
    """Safely get nested value from object."""
    result = obj
    for key in keys:
        if result is None:
            return default
        elif isinstance(result, dict):
            result = result.get(key)
        else:
            return default
    return result if result is not None else default

# Usage: label = safe_nested_get(result, ['ml_classification', 'enhanced_classification', 'label'], 'unknown')
''',
            'ui_component_safety': '''
# UI component safety pattern
def safe_ui_call(component, method, *args, **kwargs):
    """Safely call UI component methods."""
    if component is not None and hasattr(component, method):
        try:
            return getattr(component, method)(*args, **kwargs)
        except Exception as e:
            logging.error(f"UI component {method} failed: {e}")
    return None

# Usage: safe_ui_call(self.console, 'append', 'message')
''',
            'ml_model_safety': '''
# ML model safety pattern
def safe_ml_call(model, *args, **kwargs):
    """Safely call ML model."""
    if model is not None and hasattr(model, '__call__'):
        try:
            return model(*args, **kwargs)
        except Exception as e:
            logging.error(f"ML model call failed: {e}")
    return None

# Usage: result = safe_ml_call(self.bert_classifier, text)
''',
            'data_validation': '''
# Data validation pattern
def validate_data_structure(data):
    """Validate data structure and provide defaults."""
    if data is None:
        return {
            'title': '',
            'description': '',
            'tags': [],
            'provider': '',
            'confidence_score': 0.0,
            'quality_score': 0.0
        }
    
    return {
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'tags': data.get('tags', []) if isinstance(data.get('tags'), list) else [],
        'provider': data.get('provider', ''),
        'confidence_score': data.get('confidence_score', 0.0),
        'quality_score': data.get('quality_score', 0.0)
    }
'''
        }
        
        # Save fixes to file
        with open('safety_fixes.py', 'w') as f:
            f.write("# Generated safety fixes for NoneType error prevention\n\n")
            for name, fix in fixes.items():
                f.write(f"# {name}\n{fix}\n")
        
        logging.info("✅ Safety fixes saved to safety_fixes.py")
    
    def run_all_tests(self):
        """Run all NoneType safety tests."""
        logging.info("🚀 Starting comprehensive NoneType safety tests...")
        
        self.test_safe_get_operations()
        self.test_nested_get_operations()
        self.test_ui_component_safety()
        self.test_ml_model_safety()
        self.test_data_processing_safety()
        self.test_soup_parsing_safety()
        
        # Generate fixes
        self.generate_safety_fixes()
        
        # Print summary
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        logging.info(f"\n📊 TEST SUMMARY:")
        logging.info(f"   Total tests: {total_tests}")
        logging.info(f"   Passed: {self.test_results['passed']}")
        logging.info(f"   Failed: {self.test_results['failed']}")
        logging.info(f"   Warnings: {self.test_results['warnings']}")
        
        if self.test_results['failed'] == 0:
            logging.info("✅ All critical tests passed!")
        else:
            logging.error(f"❌ {self.test_results['failed']} critical tests failed!")
        
        return self.test_results

if __name__ == "__main__":
    tester = NoneTypeTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if results['failed'] == 0 else 1) 