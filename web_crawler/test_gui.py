#!/usr/bin/env python3
"""
Simple GUI test
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

def test_gui():
    """Test basic GUI functionality"""
    print("🧪 Testing GUI...")
    
    try:
        app = QApplication(sys.argv)
        print("✅ QApplication created")
        
        # Create a simple window
        window = QMainWindow()
        window.setWindowTitle("Test Window")
        window.setGeometry(100, 100, 400, 300)
        
        # Add a label
        central_widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel("Test GUI Window - If you can see this, GUI is working!")
        layout.addWidget(label)
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)
        
        # Show the window
        window.show()
        print("✅ Window shown")
        
        # Run the event loop
        print("🔄 Starting event loop...")
        result = app.exec()
        print(f"✅ Event loop finished with result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        print(f"❌ Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("🚀 Starting GUI test...")
    if test_gui():
        print("✅ GUI test passed!")
    else:
        print("❌ GUI test failed!")
        sys.exit(1) 