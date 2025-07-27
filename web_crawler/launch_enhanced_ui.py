#!/usr/bin/env python3
"""
Launcher script for the Enhanced Web Crawler UI with Output Directory Feature
"""

import sys
import os

def main():
    print("🚀 Launching Enhanced Web Crawler UI with Output Directory Feature")
    print("=" * 70)
    
    # Check if we're in the right directory
    if not os.path.exists("enhanced_crawler_ui.py"):
        print("❌ Error: enhanced_crawler_ui.py not found in current directory")
        print("Please run this script from the web_crawler directory")
        return 1
    
    # Check for required dependencies
    try:
        import PySide6
        print("✓ PySide6 is available")
    except ImportError:
        print("❌ Error: PySide6 is not installed")
        print("Please install PySide6: pip install PySide6")
        return 1
    
    try:
        import enhanced_crawler_ui
        print("✓ Enhanced crawler UI module loaded successfully")
    except ImportError as e:
        print(f"❌ Error loading enhanced crawler UI: {e}")
        return 1
    
    # Check if output directory feature is present
    if hasattr(enhanced_crawler_ui.EnhancedCrawlerUI, 'browse_output_directory'):
        print("✓ Output directory feature is present")
    else:
        print("❌ Warning: Output directory feature not found")
    
    print("\n🎯 Starting Enhanced Web Crawler UI...")
    print("Look for the 'Output Directory Settings' section in the UI")
    print("=" * 70)
    
    # Launch the UI
    try:
        from PySide6.QtWidgets import QApplication
        import enhanced_crawler_ui
        
        # Create application
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create and show UI
        ui = enhanced_crawler_ui.EnhancedCrawlerUI()
        ui.show()
        
        print("✅ Enhanced Web Crawler UI launched successfully!")
        print("📁 Output Directory Settings should be visible in the UI")
        
        # Run the application
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 