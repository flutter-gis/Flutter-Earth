#!/usr/bin/env python3
"""
Comprehensive Debug Script for Enhanced Web Crawler
Tests all components and connections systematically
"""

import sys
import os
import time
import gc
import logging
from datetime import datetime

# Setup logging for debug
logging.basicConfig(
    filename='comprehensive_debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_basic_imports():
    """Test all basic imports"""
    print("🔍 Testing basic imports...")
    logging.info("Starting basic imports test")
    
    basic_modules = [
        ('sys', 'System module'),
        ('os', 'OS module'),
        ('time', 'Time module'),
        ('json', 'JSON module'),
        ('yaml', 'YAML module'),
        ('threading', 'Threading module'),
        ('asyncio', 'AsyncIO module'),
        ('requests', 'Requests module'),
        ('sqlite3', 'SQLite module'),
        ('importlib.util', 'ImportLib module'),
        ('datetime', 'DateTime module'),
        ('dataclasses', 'DataClasses module'),
        ('typing', 'Typing module'),
        ('concurrent.futures', 'Concurrent Futures module'),
        ('urllib.parse', 'URL Parse module'),
        ('psutil', 'PSUtil module'),
        ('collections', 'Collections module'),
        ('queue', 'Queue module'),
        ('gc', 'Garbage Collection module'),
        ('signal', 'Signal module'),
    ]
    
    results = []
    for module, desc in basic_modules:
        try:
            __import__(module)
            print(f"✅ {desc}")
            results.append(('PASS', module, desc))
            logging.info(f"Basic import PASS: {module}")
        except Exception as e:
            print(f"❌ {desc}: {e}")
            results.append(('FAIL', module, desc, str(e)))
            logging.error(f"Basic import FAIL: {module} - {e}")
    
    return results

def test_pyside6_imports():
    """Test PySide6 imports"""
    print("\n🔍 Testing PySide6 imports...")
    logging.info("Starting PySide6 imports test")
    
    pyside_modules = [
        ('PySide6.QtWidgets', 'PySide6 QtWidgets'),
        ('PySide6.QtCore', 'PySide6 QtCore'),
        ('PySide6.QtGui', 'PySide6 QtGui'),
    ]
    
    results = []
    for module, desc in pyside_modules:
        try:
            __import__(module)
            print(f"✅ {desc}")
            results.append(('PASS', module, desc))
            logging.info(f"PySide6 import PASS: {module}")
        except Exception as e:
            print(f"❌ {desc}: {e}")
            results.append(('FAIL', module, desc, str(e)))
            logging.error(f"PySide6 import FAIL: {module} - {e}")
    
    return results

def test_ml_imports():
    """Test ML-related imports"""
    print("\n🔍 Testing ML imports...")
    logging.info("Starting ML imports test")
    
    ml_modules = [
        ('spacy', 'spaCy'),
        ('transformers', 'Transformers'),
        ('torch', 'PyTorch'),
        ('sklearn', 'Scikit-learn'),
        ('geopy', 'Geopy'),
        ('pytesseract', 'Pytesseract'),
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('plotly', 'Plotly'),
    ]
    
    results = []
    for module, desc in ml_modules:
        try:
            __import__(module)
            print(f"✅ {desc}")
            results.append(('PASS', module, desc))
            logging.info(f"ML import PASS: {module}")
        except Exception as e:
            print(f"❌ {desc}: {e}")
            results.append(('FAIL', module, desc, str(e)))
            logging.error(f"ML import FAIL: {module} - {e}")
    
    return results

def test_local_modules():
    """Test local module imports"""
    print("\n🔍 Testing local modules...")
    logging.info("Starting local modules test")
    
    local_modules = [
        ('ai_content_enhancer', 'AI Content Enhancer'),
        ('real_time_collaboration', 'Real Time Collaboration'),
        ('advanced_data_explorer', 'Advanced Data Explorer'),
        ('advanced_automation', 'Advanced Automation'),
        ('web_validation', 'Web Validation'),
        ('crash_prevention_system', 'Crash Prevention System'),
        ('enhanced_crawler_ui', 'Enhanced Crawler UI'),
    ]
    
    results = []
    for module, desc in local_modules:
        try:
            __import__(module)
            print(f"✅ {desc}")
            results.append(('PASS', module, desc))
            logging.info(f"Local module PASS: {module}")
        except Exception as e:
            print(f"❌ {desc}: {e}")
            results.append(('FAIL', module, desc, str(e)))
            logging.error(f"Local module FAIL: {module} - {e}")
    
    return results

def test_memory_safety():
    """Test memory safety functions"""
    print("\n🔍 Testing memory safety...")
    logging.info("Starting memory safety test")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        print(f"✅ Memory check: {memory.percent}% used")
        logging.info(f"Memory check: {memory.percent}% used")
        
        if memory.percent > 85:
            print("⚠️ High memory usage detected")
            logging.warning(f"High memory usage: {memory.percent}%")
            return [('WARN', 'memory', f"High usage: {memory.percent}%")]
        else:
            print("✅ Memory usage acceptable")
            return [('PASS', 'memory', f"Usage: {memory.percent}%")]
            
    except Exception as e:
        print(f"❌ Memory check failed: {e}")
        logging.error(f"Memory check failed: {e}")
        return [('FAIL', 'memory', str(e))]

def test_config_files():
    """Test configuration files"""
    print("\n🔍 Testing configuration files...")
    logging.info("Starting configuration files test")
    
    config_files = [
        ('crawler_config.yaml', 'Crawler Config'),
        ('requirements_crawler.txt', 'Requirements'),
        ('requirements_dashboard.txt', 'Dashboard Requirements'),
    ]
    
    results = []
    for filename, desc in config_files:
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                print(f"✅ {desc}: {len(content)} bytes")
                results.append(('PASS', filename, desc, f"{len(content)} bytes"))
                logging.info(f"Config file PASS: {filename}")
            except Exception as e:
                print(f"❌ {desc}: {e}")
                results.append(('FAIL', filename, desc, str(e)))
                logging.error(f"Config file FAIL: {filename} - {e}")
        else:
            print(f"❌ {desc}: File not found")
            results.append(('FAIL', filename, desc, 'File not found'))
            logging.error(f"Config file not found: {filename}")
    
    return results

def test_ui_components():
    """Test UI component creation"""
    print("\n🔍 Testing UI components...")
    logging.info("Starting UI components test")
    
    try:
        from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QFont
        
        # Create minimal app
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Test basic widget creation
        widget = QWidget()
        layout = QVBoxLayout()
        button = QPushButton("Test")
        label = QLabel("Test Label")
        
        layout.addWidget(button)
        layout.addWidget(label)
        widget.setLayout(layout)
        
        print("✅ Basic UI components created successfully")
        logging.info("UI components test PASS")
        
        # Clean up
        widget.deleteLater()
        
        return [('PASS', 'ui_components', 'Basic UI components')]
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        logging.error(f"UI components test FAIL: {e}")
        return [('FAIL', 'ui_components', str(e))]

def test_crawler_ui_import():
    """Test importing the main crawler UI"""
    print("\n🔍 Testing crawler UI import...")
    logging.info("Starting crawler UI import test")
    
    try:
        # Import the main class
        from enhanced_crawler_ui import EnhancedCrawlerUI, check_memory_safety, safe_ml_operation
        
        print("✅ EnhancedCrawlerUI class imported successfully")
        print("✅ check_memory_safety function available")
        print("✅ safe_ml_operation function available")
        
        logging.info("Crawler UI import test PASS")
        return [('PASS', 'crawler_ui_import', 'Main UI class imported')]
        
    except Exception as e:
        print(f"❌ Crawler UI import failed: {e}")
        logging.error(f"Crawler UI import FAIL: {e}")
        return [('FAIL', 'crawler_ui_import', str(e))]

def test_advanced_features():
    """Test advanced features availability"""
    print("\n🔍 Testing advanced features...")
    logging.info("Starting advanced features test")
    
    try:
        from enhanced_crawler_ui import (
            AI_ENHANCER_AVAILABLE, COLLABORATION_AVAILABLE, 
            DATA_EXPLORER_AVAILABLE, AUTOMATION_AVAILABLE, 
            WEB_VALIDATION_AVAILABLE, CRASH_PREVENTION_AVAILABLE
        )
        
        features = [
            ('AI_ENHANCER_AVAILABLE', AI_ENHANCER_AVAILABLE),
            ('COLLABORATION_AVAILABLE', COLLABORATION_AVAILABLE),
            ('DATA_EXPLORER_AVAILABLE', DATA_EXPLORER_AVAILABLE),
            ('AUTOMATION_AVAILABLE', AUTOMATION_AVAILABLE),
            ('WEB_VALIDATION_AVAILABLE', WEB_VALIDATION_AVAILABLE),
            ('CRASH_PREVENTION_AVAILABLE', CRASH_PREVENTION_AVAILABLE),
        ]
        
        results = []
        for name, available in features:
            status = "✅" if available else "❌"
            print(f"{status} {name}: {available}")
            results.append(('PASS' if available else 'FAIL', name, str(available)))
            logging.info(f"Advanced feature {name}: {available}")
        
        return results
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        logging.error(f"Advanced features test FAIL: {e}")
        return [('FAIL', 'advanced_features', str(e))]

def generate_debug_report(all_results):
    """Generate comprehensive debug report"""
    print("\n" + "="*60)
    print("🔍 COMPREHENSIVE DEBUG REPORT")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warning_tests = 0
    
    for category, results in all_results.items():
        print(f"\n📊 {category.upper()}:")
        for result in results:
            total_tests += 1
            if result[0] == 'PASS':
                passed_tests += 1
                print(f"  ✅ {result[2]}")
            elif result[0] == 'FAIL':
                failed_tests += 1
                print(f"  ❌ {result[2]}: {result[3] if len(result) > 3 else 'Unknown error'}")
            elif result[0] == 'WARN':
                warning_tests += 1
                print(f"  ⚠️ {result[2]}: {result[3] if len(result) > 3 else 'Warning'}")
    
    print(f"\n📈 SUMMARY:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed_tests}")
    print(f"  Failed: {failed_tests}")
    print(f"  Warnings: {warning_tests}")
    print(f"  Success Rate: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    # Log summary
    logging.info(f"Debug report - Total: {total_tests}, Passed: {passed_tests}, Failed: {failed_tests}, Warnings: {warning_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready.")
        logging.info("All debug tests passed - system is ready")
    else:
        print(f"\n⚠️ {failed_tests} tests failed. Check logs for details.")
        logging.warning(f"{failed_tests} debug tests failed")

def main():
    """Main debug function"""
    print("🚀 Starting Comprehensive Debug...")
    logging.info("Starting comprehensive debug session")
    
    all_results = {}
    
    # Run all tests
    all_results['Basic Imports'] = test_basic_imports()
    all_results['PySide6 Imports'] = test_pyside6_imports()
    all_results['ML Imports'] = test_ml_imports()
    all_results['Local Modules'] = test_local_modules()
    all_results['Memory Safety'] = test_memory_safety()
    all_results['Config Files'] = test_config_files()
    all_results['UI Components'] = test_ui_components()
    all_results['Crawler UI Import'] = test_crawler_ui_import()
    all_results['Advanced Features'] = test_advanced_features()
    
    # Generate report
    generate_debug_report(all_results)
    
    print(f"\n📝 Debug log saved to: comprehensive_debug.log")
    print("🔍 Check the log file for detailed information")

if __name__ == "__main__":
    main() 