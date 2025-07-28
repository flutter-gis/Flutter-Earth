# Crawler Crash Fix Guide

## Crash Analysis Results

### Identified Issues:
1. **Qt6Core.dll Access Violation** (0xc0000005)
2. **Heap Corruption** (0xc0000374) 
3. **Missing Dependencies**
4. **Memory Management Problems**

## Immediate Fixes

### 1. Fix PySide6/Qt6 Issues
```bash
# Uninstall and reinstall PySide6
pip uninstall PySide6
pip install PySide6==6.5.0

# Alternative: Use PyQt6 instead
pip uninstall PySide6
pip install PyQt6
```

### 2. Install Missing Dependencies
```bash
pip install beautifulsoup4
pip install lxml
pip install spacy
python -m spacy download en_core_web_sm
```

### 3. Memory Management Fixes

#### Create a memory-safe launcher:
```python
# safe_launcher.py
import gc
import psutil
import sys
from PySide6.QtWidgets import QApplication

def check_memory():
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        print("⚠️ High memory usage detected")
        gc.collect()
        return False
    return True

def main():
    # Force garbage collection before starting
    gc.collect()
    
    # Check memory before starting
    if not check_memory():
        print("❌ Insufficient memory available")
        return 1
    
    app = QApplication(sys.argv)
    
    # Import UI only after memory check
    try:
        from enhanced_crawler_ui import EnhancedCrawlerUI
        window = EnhancedCrawlerUI()
        window.show()
        return app.exec()
    except Exception as e:
        print(f"❌ Failed to start UI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### 4. Disable Heavy ML Models Temporarily

Edit `enhanced_crawler_ui.py` and comment out these imports:
```python
# Comment out these lines temporarily:
# try:
#     from ai_content_enhancer import AIContentEnhancer
#     AI_ENHANCER_AVAILABLE = True
# except ImportError:
#     AI_ENHANCER_AVAILABLE = False

# Set all to False for testing:
AI_ENHANCER_AVAILABLE = False
COLLABORATION_AVAILABLE = False
DATA_EXPLORER_AVAILABLE = False
AUTOMATION_AVAILABLE = False
WEB_VALIDATION_AVAILABLE = False
```

### 5. Create a Minimal Test Version

```python
# minimal_test.py
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

class MinimalTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minimal Crawler Test")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Test basic UI
        label = QLabel("Crawler UI Test - If you see this, PySide6 works!")
        layout.addWidget(label)
        
        # Test button
        btn = QPushButton("Test Button")
        btn.clicked.connect(self.test_click)
        layout.addWidget(btn)
        
        self.setLayout(layout)
    
    def test_click(self):
        print("✅ Button click works!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MinimalTest()
    window.show()
    sys.exit(app.exec())
```

## Testing Steps

### Step 1: Test PySide6
```bash
cd web_crawler
python minimal_test.py
```

### Step 2: Test Basic Imports
```bash
python test_imports.py
```

### Step 3: Test with Disabled ML
```bash
# Edit enhanced_crawler_ui.py to disable ML imports
python enhanced_crawler_ui.py
```

### Step 4: Full Test
```bash
# After fixing dependencies
python safe_launcher.py
```

## Prevention Measures

### 1. Add Memory Monitoring
```python
def monitor_memory():
    memory = psutil.virtual_memory()
    if memory.percent > 85:
        print("⚠️ CRITICAL: Memory usage too high!")
        return False
    return True
```

### 2. Add Crash Recovery
```python
def safe_execute(func):
    try:
        return func()
    except Exception as e:
        print(f"❌ Function crashed: {e}")
        return None
```

### 3. Add Logging
```python
import logging
logging.basicConfig(
    filename='crawler_crash.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Expected Results

After applying these fixes:
1. ✅ PySide6 should load without crashes
2. ✅ Memory usage should be stable
3. ✅ Basic UI should work
4. ✅ Crawler should start without immediate crashes

## Next Steps

1. Test the minimal version first
2. Gradually re-enable features
3. Monitor memory usage during crawling
4. Add proper error handling and logging 