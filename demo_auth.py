#!/usr/bin/env python3
"""Demo script for testing the Earth Engine authentication system."""

import sys
import os
from PyQt5 import QtWidgets

# Add the dead_the_third package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dead_the_third'))

def test_auth_dialog():
    """Test the authentication setup dialog."""
    # Set environment variable to avoid WebEngine issues
    os.environ['QT_WEBENGINE_DISABLE_SANDBOX'] = '1'
    
    app = QtWidgets.QApplication(sys.argv)
    
    from dead_the_third.auth_setup import AuthSetupDialog
    
    dialog = AuthSetupDialog()
    result = dialog.exec_()
    
    if result == QtWidgets.QDialog.Accepted:
        credentials = dialog.get_credentials()
        print("✅ Authentication setup completed!")
        print(f"Project ID: {credentials['project_id']}")
        print(f"Key file: {credentials['key_file']}")
    else:
        print("❌ Authentication setup cancelled")
    
    return result == QtWidgets.QDialog.Accepted

def test_auth_manager():
    """Test the authentication manager."""
    from dead_the_third.auth_setup import AuthManager
    
    auth_manager = AuthManager()
    
    print("Testing authentication manager...")
    print(f"Has credentials: {auth_manager.has_credentials()}")
    
    if auth_manager.has_credentials():
        credentials = auth_manager.load_credentials()
        print(f"Loaded credentials: {credentials}")
        
        # Test Earth Engine initialization
        if auth_manager.initialize_earth_engine():
            print("✅ Earth Engine initialized successfully!")
            return True
        else:
            print("❌ Earth Engine initialization failed")
            return False
    else:
        print("No stored credentials found")
        return False

def main():
    """Main demo function."""
    print("Earth Engine Authentication Demo")
    print("=" * 40)
    
    # Test 1: Authentication dialog
    print("\n1. Testing authentication dialog...")
    if test_auth_dialog():
        print("✅ Dialog test passed")
    else:
        print("❌ Dialog test failed")
    
    # Test 2: Authentication manager
    print("\n2. Testing authentication manager...")
    if test_auth_manager():
        print("✅ Manager test passed")
    else:
        print("❌ Manager test failed")
    
    print("\nDemo completed!")

if __name__ == "__main__":
    main() 