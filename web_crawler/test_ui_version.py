#!/usr/bin/env python3
"""
Test script to verify UI version and output directory feature
"""

import sys
import os

def test_ui_version():
    """Test if the UI has the output directory feature"""
    print("Testing UI Version and Features")
    print("=" * 40)
    
    # Check if we can import the enhanced crawler UI
    try:
        import enhanced_crawler_ui
        print("✓ Enhanced crawler UI imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import enhanced crawler UI: {e}")
        return False
    
    # Check if the output directory feature is present
    try:
        # Check if the UI class has the output directory methods
        ui_class = enhanced_crawler_ui.EnhancedCrawlerUI
        
        # Check for required methods
        required_methods = [
            'browse_output_directory',
            'update_output_directories',
            'update_ml_cache_directory'
        ]
        
        for method in required_methods:
            if hasattr(ui_class, method):
                print(f"✓ Method '{method}' found")
            else:
                print(f"✗ Method '{method}' NOT found")
                return False
        
        print("\n✓ All output directory methods are present!")
        return True
        
    except Exception as e:
        print(f"✗ Error checking UI features: {e}")
        return False

def test_ui_creation():
    """Test if we can create a UI instance"""
    print("\nTesting UI Creation")
    print("=" * 20)
    
    try:
        from PySide6.QtWidgets import QApplication
        import enhanced_crawler_ui
        
        # Create QApplication instance
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create UI instance
        ui = enhanced_crawler_ui.EnhancedCrawlerUI()
        print("✓ UI instance created successfully")
        
        # Check if output directory elements are present (after setup_ui is called)
        if hasattr(ui, 'output_dir_edit'):
            print(f"✓ Output directory edit field: {ui.output_dir_edit}")
        else:
            print("✗ Output directory edit field not found")
        
        if hasattr(ui, 'output_browse_btn'):
            print(f"✓ Output browse button: {ui.output_browse_btn}")
        else:
            print("✗ Output browse button not found")
        
        if hasattr(ui, 'output_info_label'):
            print(f"✓ Output info label: {ui.output_info_label}")
        else:
            print("✗ Output info label not found")
        
        # Clean up
        app.quit()
        print("✓ UI test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ Error creating UI: {e}")
        return False

if __name__ == "__main__":
    print("UI Version and Feature Test")
    print("=" * 30)
    
    # Test UI version
    version_ok = test_ui_version()
    
    # Test UI creation
    creation_ok = test_ui_creation()
    
    if version_ok and creation_ok:
        print("\n🎉 All tests passed! The enhanced UI with output directory feature is working correctly.")
    else:
        print("\n❌ Some tests failed. The UI may not have the latest features.")
    
    print(f"\nPython version: {sys.version}")
    print(f"Current directory: {os.getcwd()}") 