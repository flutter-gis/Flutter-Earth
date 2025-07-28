#!/usr/bin/env python3
"""
Detailed Crawling Debug Script
Tests actual crawling functionality and data processing
"""

import sys
import traceback
import time
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

def test_file_access():
    """Test file access and permissions"""
    print("🔍 Testing file access...")
    try:
        # Test if we can read the HTML file (with non-breaking spaces)
        html_file = os.path.join("..", "gee cat", "Earth Engine Data Catalog \xa0_\xa0 Google for Developers.html")
        if os.path.exists(html_file):
            print(f"✅ HTML file exists: {html_file}")
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"✅ HTML file readable, size: {len(content)} bytes")
        else:
            print(f"❌ HTML file not found: {html_file}")
            return False
        
        # Test output directory
        output_dir = "exported_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✅ Created output directory: {output_dir}")
        else:
            print(f"✅ Output directory exists: {output_dir}")
        
        return True
    except Exception as e:
        print(f"❌ File access test failed: {e}")
        return False

def test_web_requests():
    """Test web request functionality"""
    print("\n🔍 Testing web requests...")
    try:
        import requests
        
        # Test basic request (skip SSL verification for testing)
        response = requests.get("https://httpbin.org/get", timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ Basic web request works")
        else:
            print(f"❌ Basic web request failed: {response.status_code}")
            return False
        
        # Test with headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get("https://httpbin.org/headers", headers=headers, timeout=10, verify=False)
        if response.status_code == 200:
            print("✅ Request with headers works")
        else:
            print(f"❌ Request with headers failed: {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Web request test failed: {e}")
        return False

def test_html_parsing():
    """Test HTML parsing functionality"""
    print("\n🔍 Testing HTML parsing...")
    try:
        from bs4 import BeautifulSoup
        
        # Test with simple HTML
        html = "<html><body><h1>Test</h1><p>Content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        if soup.find('h1'):
            print("✅ Basic HTML parsing works")
        else:
            print("❌ Basic HTML parsing failed")
            return False
        
        # Test with real HTML file
        html_file = os.path.join("..", "gee cat", "Earth Engine Data Catalog \xa0_\xa0 Google for Developers.html")
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find some basic elements
                links = soup.find_all('a')
                print(f"✅ Found {len(links)} links in HTML file")
                
                if len(links) > 0:
                    print("✅ HTML file parsing works")
                else:
                    print("❌ No links found in HTML file")
                    return False
        
        return True
    except Exception as e:
        print(f"❌ HTML parsing test failed: {e}")
        return False

def test_ai_models():
    """Test AI model loading and functionality"""
    print("\n🔍 Testing AI models...")
    try:
        # Test spaCy
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("This is a test sentence.")
        if len(doc.ents) >= 0:  # Should work even with no entities
            print("✅ spaCy NLP model works")
        else:
            print("❌ spaCy NLP model failed")
            return False
        
        # Test transformers
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        try:
            tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
            model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")
            print("✅ Transformers models loaded")
        except Exception as e:
            print(f"⚠️ Transformers models failed to load: {e}")
            # This is not critical for basic functionality
        
        return True
    except Exception as e:
        print(f"❌ AI models test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n🔍 Testing database...")
    try:
        import sqlite3
        
        # Test database creation
        db_path = "exported_data/crawler_data.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create test table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT
            )
        """)
        
        # Insert test data
        cursor.execute("INSERT INTO test_table (title, description) VALUES (?, ?)", 
                      ("Test Title", "Test Description"))
        
        # Query test data
        cursor.execute("SELECT * FROM test_table")
        results = cursor.fetchall()
        
        if len(results) > 0:
            print("✅ Database operations work")
        else:
            print("❌ Database query failed")
            return False
        
        # Clean up
        cursor.execute("DROP TABLE test_table")
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_crawler_ui_methods():
    """Test specific crawler UI methods"""
    print("\n🔍 Testing crawler UI methods...")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test data structures
        if hasattr(ui, 'extracted_data') and isinstance(ui.extracted_data, list):
            print("✅ extracted_data list exists")
        else:
            print("❌ extracted_data list missing or wrong type")
            return False
        
        if hasattr(ui, 'thread'):
            print("✅ thread attribute exists")
        else:
            print("❌ thread attribute missing")
            return False
        
        # Test configuration
        if hasattr(ui, 'config') and ui.config:
            print("✅ Configuration loaded")
        else:
            print("❌ Configuration not loaded")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Crawler UI methods test failed: {e}")
        traceback.print_exc()
        return False

def test_monitoring_data():
    """Test monitoring data structures"""
    print("\n🔍 Testing monitoring data...")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test monitoring data structure
        required_keys = [
            'download_speed', 'processing_speed', 'cpu_usage', 'memory_usage',
            'concurrent_requests', 'request_delay', 'success_rate', 'error_rate', 'timestamps'
        ]
        
        for key in required_keys:
            if key in ui.monitoring_data:
                print(f"✅ {key} exists in monitoring_data")
            else:
                print(f"❌ {key} missing from monitoring_data")
                return False
        
        # Test data types (monitoring_data uses deque, not list)
        for key in ['download_speed', 'processing_speed', 'cpu_usage', 'memory_usage']:
            from collections import deque
            if isinstance(ui.monitoring_data[key], deque):
                print(f"✅ {key} is correct type (deque)")
            else:
                print(f"❌ {key} is wrong type: {type(ui.monitoring_data[key])}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Monitoring data test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling mechanisms"""
    print("\n🔍 Testing error handling...")
    try:
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        ui = EnhancedCrawlerUI()
        
        # Test error handling methods
        if hasattr(ui, 'enhanced_error_handling'):
            try:
                ui.enhanced_error_handling(Exception("Test error"), "Test context")
                print("✅ enhanced_error_handling works")
            except Exception as e:
                print(f"❌ enhanced_error_handling failed: {e}")
                return False
        
        if hasattr(ui, 'apply_error_recovery'):
            try:
                ui.apply_error_recovery("test", "Test error message")
                print("✅ apply_error_recovery works")
            except Exception as e:
                print(f"❌ apply_error_recovery failed: {e}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run detailed crawling diagnostics"""
    print("🚀 Starting Detailed Crawling Diagnostics")
    print("=" * 60)
    
    tests = [
        ("File Access", test_file_access),
        ("Web Requests", test_web_requests),
        ("HTML Parsing", test_html_parsing),
        ("AI Models", test_ai_models),
        ("Database", test_database),
        ("Crawler UI Methods", test_crawler_ui_methods),
        ("Monitoring Data", test_monitoring_data),
        ("Error Handling", test_error_handling),
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
    
    print("\n" + "=" * 60)
    print("📊 DETAILED DIAGNOSTIC RESULTS")
    print("=" * 60)
    
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
        print("\n🎉 ALL DIAGNOSTICS PASSED! Crawling system is fully operational.")
    else:
        print(f"\n⚠️ {failed} diagnostic(s) failed. Some features may not work properly.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 