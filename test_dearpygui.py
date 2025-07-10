#!/usr/bin/env python3
"""
Test script for Dear PyGui functionality
"""

import sys
import os

def test_dearpygui_import():
    """Test if Dear PyGui can be imported"""
    try:
        import dearpygui.dearpygui as dpg
        print("✓ Dear PyGui imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Dear PyGui: {e}")
        return False

def test_dearpygui_basic():
    """Test basic Dear PyGui functionality"""
    try:
        import dearpygui.dearpygui as dpg
        
        # Create context
        dpg.create_context()
        print("✓ Dear PyGui context created")
        
        # Create viewport
        dpg.create_viewport(title="Test", width=400, height=300)
        print("✓ Dear PyGui viewport created")
        
        # Create simple window
        with dpg.window(label="Test Window"):
            dpg.add_text("Hello, Dear PyGui!")
            dpg.add_button(label="Test Button")
        
        print("✓ Dear PyGui window created")
        
        # Setup and show
        dpg.setup_dearpygui()
        dpg.show_viewport()
        
        # Cleanup
        dpg.destroy_context()
        print("✓ Dear PyGui test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Dear PyGui test failed: {e}")
        return False

def test_requirements():
    """Test if all required packages can be imported"""
    packages = [
        "numpy",
        "matplotlib", 
        "requests",
        "json",
        "pathlib"
    ]
    
    all_good = True
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package} imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import {package}: {e}")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("Testing Dear PyGui Setup...")
    print("=" * 40)
    
    # Test imports
    print("\n1. Testing package imports:")
    req_ok = test_requirements()
    
    print("\n2. Testing Dear PyGui import:")
    dpg_import_ok = test_dearpygui_import()
    
    print("\n3. Testing Dear PyGui basic functionality:")
    dpg_basic_ok = test_dearpygui_basic()
    
    print("\n" + "=" * 40)
    print("Test Results:")
    print(f"Requirements: {'✓ PASS' if req_ok else '✗ FAIL'}")
    print(f"Dear PyGui Import: {'✓ PASS' if dpg_import_ok else '✗ FAIL'}")
    print(f"Dear PyGui Basic: {'✓ PASS' if dpg_basic_ok else '✗ FAIL'}")
    
    if all([req_ok, dpg_import_ok, dpg_basic_ok]):
        print("\n🎉 All tests passed! Dear PyGui is ready to use.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 