import sys
import os
import threading
from queue import Queue
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QProgressBar, QLabel
)
from PySide6.QtCore import QTimer, Qt

# Import or define your crawler here
# from your_crawler_module import crawl_catalog
# For demonstration, we'll use a dummy function

def crawl_catalog(log_queue, progress_queue):
    import time
    total = 100
    for i in range(total):
        log_queue.put(f"[INFO] Crawling dataset {i+1}/{total}")
        progress_queue.put(i+1)
        time.sleep(0.05)
    log_queue.put("[DONE] Crawling complete.")
    progress_queue.put(total)

class CrawlerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Earth Engine Catalog Web Crawler")
        self.resize(800, 500)
        layout = QVBoxLayout(self)
        self.status = QLabel("Ready.")
        layout.addWidget(self.status)
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setStyleSheet("background: #181818; color: #e0e0e0; font-family: Consolas;")
        layout.addWidget(self.console, 1)
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setStyleSheet("QProgressBar {height: 30px; font-size: 16px;} QProgressBar::chunk {background: #3a6ea5;}")
        layout.addWidget(self.progress)
        self.crawl_btn = QPushButton("Crawl Catalog")
        self.crawl_btn.clicked.connect(self.start_crawl)
        layout.addWidget(self.crawl_btn)
        self.log_queue = Queue()
        self.progress_queue = Queue()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.thread = None

    def start_crawl(self):
        self.console.clear()
        self.status.setText("Crawling...")
        self.progress.setValue(0)
        self.crawl_btn.setEnabled(False)
        self.thread = threading.Thread(target=crawl_catalog, args=(self.log_queue, self.progress_queue), daemon=True)
        self.thread.start()
        self.timer.start(100)

    def update_ui(self):
        while not self.log_queue.empty():
            msg = self.log_queue.get()
            self.console.append(msg)
            if "[DONE]" in msg:
                self.status.setText("Done!")
                self.crawl_btn.setEnabled(True)
        while not self.progress_queue.empty():
            val = self.progress_queue.get()
            self.progress.setValue(val)
        if not self.thread.is_alive():
            self.timer.stop()
            self.crawl_btn.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CrawlerUI()
    win.show()
    sys.exit(app.exec()) 