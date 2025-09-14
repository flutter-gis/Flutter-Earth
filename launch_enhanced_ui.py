#!/usr/bin/env python3
"""
Launch the Enhanced Flutter Earth UI with extracted Earth Engine data
"""

import os
import sys
import json
from PySide6.QtWidgets import QApplication

# Add the web_crawler directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_crawler'))

from lightweight_crawler import LocalHTMLDataExtractorUI

def main():
    print("=== FLUTTER EARTH - ENHANCED UI ===")
    print("Launching with extracted Earth Engine data...")

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Set application properties
    app.setApplicationName("Flutter Earth - Enhanced Satellite Catalog Viewer")
    app.setApplicationVersion("3.0")
    app.setOrganizationName("Flutter Earth")

    window = LocalHTMLDataExtractorUI()

    # Load the extracted data into the UI
    ui_data_file = 'web_crawler/collected_data/ui_data.json'
    if os.path.exists(ui_data_file):
        with open(ui_data_file, 'r', encoding='utf-8') as f:
            ui_data = json.load(f)

        # Add the data to the UI's extracted_data
        window.extracted_data.append(ui_data)

        # Update the UI displays
        window.update_summary_dashboard()
        window.update_catalog_table()
        window.populate_gallery()

        # Switch to the gallery tab to show the thumbnails
        window.data_viewer_tabs.setCurrentIndex(3)  # Gallery tab

        print(f"Loaded {len(ui_data['satellite_catalog']['datasets'])} datasets into UI")
        print("Gallery tab activated - you can now view dataset thumbnails!")

    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
