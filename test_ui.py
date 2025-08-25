#!/usr/bin/env python3
"""
Simple test script to check if PySide6 UI components work
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Signal

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test UI")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Test button
        test_btn = QPushButton("Test Button")
        test_btn.clicked.connect(self.test_click)
        layout.addWidget(test_btn)
        
        # Test label
        test_label = QLabel("Test Label")
        layout.addWidget(test_label)
        
        self.setLayout(layout)
    
    def test_click(self):
        print("Button clicked successfully!")
        self.close()

def main():
    app = QApplication(sys.argv)
    window = TestWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 