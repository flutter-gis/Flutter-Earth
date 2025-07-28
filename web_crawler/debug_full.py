#!/usr/bin/env python3
"""
Full Debug Script for Enhanced Web Crawler
Tests all components and identifies issues
"""

import sys
import traceback
import time
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import QTimer

def test_basic_imports():
    """Test basic imports"""
    print("🔍 Testing basic imports...")
    try:
        import requests
        print("✅ requests imported")
    except Exception as e:
        print(f"❌ requests import failed: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil imported")
    except Exception as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    try:
        import transformers
        print("✅ transformers imported")
    except Exception as e:
        print(f"❌ transformers import failed: {e}")
        return False
    
    return True

def test_ui_components():
    """Test UI components"""
    print("\n🔍 Testing UI components...")
    try:
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        # Test basic widget creation
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Test Label")
        button = QPushButton("Test Button")
        layout.addWidget(label)
        layout.addWidget(button)
        print("✅ Basic widgets created")
        
        # Test timer
        timer = QTimer()
        timer.timeout.connect(lambda: None)
        timer.start(1000)
        print("✅ QTimer created and started")
        
        app.quit()
        print("✅ UI components test passed")
        return True
        
    except Exception as e:
        print(f"❌ UI components test failed: {e}")
        traceback.print_exc()
        return False

def test_enhanced_crawler_import():
    """Test enhanced crawler import"""
    print("\n🔍 Testing enhanced crawler import...")
    try:
        from enhanced_crawler_ui import EnhancedCrawlerUI
        print("✅ EnhancedCrawlerUI imported")
        return True
    except Exception as e:
        print(f"❌ EnhancedCrawlerUI import failed: {e}")
        traceback.print_exc()
        return False

def test_ui_creation():
    """Test UI creation"""
    print("\n🔍 Testing UI creation...")
    try:
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        print("Creating EnhancedCrawlerUI instance...")
        ui = EnhancedCrawlerUI()
        print("✅ EnhancedCrawlerUI instance created")
        
        # Test basic methods
        if hasattr(ui, 'log_message'):
            ui.log_message("Test message")
            print("✅ log_message method works")
        
        if hasattr(ui, 'setup_ui'):
            print("✅ setup_ui method exists")
        
        return True
        
    except Exception as e:
        print(f"❌ UI creation failed: {e}")
        traceback.print_exc()
        return False

def test_monitoring_system():
    """Test monitoring system"""
    print("\n🔍 Testing monitoring system...")
    try:
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test monitoring data structure
        if hasattr(ui, 'monitoring_data'):
            print("✅ monitoring_data exists")
            print(f"   Keys: {list(ui.monitoring_data.keys())}")
        else:
            print("❌ monitoring_data missing")
            return False
        
        # Test monitoring display method
        if hasattr(ui, 'update_monitoring_display'):
            try:
                ui.update_monitoring_display()
                print("✅ update_monitoring_display works")
            except Exception as e:
                print(f"❌ update_monitoring_display failed: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Monitoring system test failed: {e}")
        traceback.print_exc()
        return False

def test_logging_system():
    """Test logging system"""
    print("\n🔍 Testing logging system...")
    try:
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test all logging methods
        logging_methods = ['log_message', 'log_error', 'log_ml_classification', 'log_validation']
        
        for method_name in logging_methods:
            if hasattr(ui, method_name):
                method = getattr(ui, method_name)
                try:
                    method(f"Test {method_name}")
                    print(f"✅ {method_name} works")
                except Exception as e:
                    print(f"❌ {method_name} failed: {e}")
                    return False
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Logging system test failed: {e}")
        traceback.print_exc()
        return False

def test_crawling_components():
    """Test crawling components"""
    print("\n🔍 Testing crawling components...")
    try:
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test crawling methods
        crawling_methods = [
            'start_crawl', 'crawl_html_file', 'process_dataset_link',
            'advanced_extract', 'extract_basic_info'
        ]
        
        for method_name in crawling_methods:
            if hasattr(ui, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        # Test data structures
        if hasattr(ui, 'success_count'):
            print("✅ success_count exists")
        if hasattr(ui, 'error_count'):
            print("✅ error_count exists")
        if hasattr(ui, 'warning_count'):
            print("✅ warning_count exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Crawling components test failed: {e}")
        traceback.print_exc()
        return False

def test_ai_components():
    """Test AI components"""
    print("\n🔍 Testing AI components...")
    try:
        # Check if QApplication already exists
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test AI methods
        ai_methods = [
            'apply_ml_classification', 'apply_validation', 'apply_ensemble_methods'
        ]
        
        for method_name in ai_methods:
            if hasattr(ui, method_name):
                print(f"✅ {method_name} method exists")
            else:
                print(f"❌ {method_name} method missing")
                return False
        
        # Test AI attributes
        if hasattr(ui, 'nlp'):
            print("✅ spaCy NLP model loaded")
        else:
            print("❌ spaCy NLP model not loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ AI components test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run full debug analysis"""
    print("🚀 Starting Full Debug Analysis")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("UI Components", test_ui_components),
        ("Enhanced Crawler Import", test_enhanced_crawler_import),
        ("UI Creation", test_ui_creation),
        ("Monitoring System", test_monitoring_system),
        ("Logging System", test_logging_system),
        ("Crawling Components", test_crawling_components),
        ("AI Components", test_ai_components),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 DEBUG RESULTS SUMMARY")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n📈 Total: {len(results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for use.")
    else:
        print(f"\n⚠️ {failed} test(s) failed. System may have issues.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 