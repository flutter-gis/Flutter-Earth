#!/usr/bin/env python3
"""
Test script to isolate import issues
"""

import sys
import time

def test_import(module_name, description):
    print(f"Testing import: {description}")
    start_time = time.time()
    try:
        __import__(module_name)
        elapsed = time.time() - start_time
        print(f"✓ {description} imported successfully in {elapsed:.2f}s")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"✗ {description} failed after {elapsed:.2f}s: {e}")
        return False

def main():
    print("Testing imports step by step...")
    print("=" * 50)
    
    # Test basic imports first
    basic_imports = [
        ("sys", "System module"),
        ("os", "OS module"),
        ("time", "Time module"),
        ("json", "JSON module"),
        ("yaml", "YAML module"),
        ("threading", "Threading module"),
        ("asyncio", "AsyncIO module"),
        ("requests", "Requests module"),
        ("sqlite3", "SQLite module"),
        ("importlib.util", "ImportLib module"),
        ("datetime", "DateTime module"),
        ("dataclasses", "DataClasses module"),
        ("typing", "Typing module"),
        ("concurrent.futures", "Concurrent Futures module"),
        ("urllib.parse", "URL Parse module"),
        ("psutil", "PSUtil module"),
        ("collections", "Collections module"),
    ]
    
    for module, desc in basic_imports:
        test_import(module, desc)
    
    print("\nTesting PySide6 imports...")
    pyside_imports = [
        ("PySide6.QtWidgets", "PySide6 QtWidgets"),
        ("PySide6.QtCore", "PySide6 QtCore"),
        ("PySide6.QtGui", "PySide6 QtGui"),
    ]
    
    for module, desc in pyside_imports:
        test_import(module, desc)
    
    print("\nTesting local module imports...")
    local_imports = [
        ("ai_content_enhancer", "AI Content Enhancer"),
        ("real_time_collaboration", "Real Time Collaboration"),
        ("advanced_data_explorer", "Advanced Data Explorer"),
        ("advanced_automation", "Advanced Automation"),
        ("web_validation", "Web Validation"),
        ("crash_prevention_system", "Crash Prevention System"),
    ]
    
    for module, desc in local_imports:
        test_import(module, desc)
    
    print("\nTesting ML-related imports...")
    ml_imports = [
        ("spacy", "spaCy"),
        ("transformers", "Transformers"),
        ("torch", "PyTorch"),
        ("sklearn", "Scikit-learn"),
        ("geopy", "Geopy"),
        ("pytesseract", "Pytesseract"),
    ]
    
    for module, desc in ml_imports:
        test_import(module, desc)
    
    print("\nImport testing completed!")

if __name__ == "__main__":
    main() 