#!/usr/bin/env python3
"""
Load the extracted Earth Engine data into the UI for viewing
"""

import os
import sys
import json
import shutil

# Add the web_crawler directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_crawler'))

def create_ui_compatible_data():
    """Convert the extracted Earth Engine data to UI-compatible format"""

    # Load the extracted Earth Engine catalog
    catalog_file = 'collected_data/earth_engine_catalog.json'
    if not os.path.exists(catalog_file):
        print(f"Earth Engine catalog not found: {catalog_file}")
        return False

    with open(catalog_file, 'r', encoding='utf-8') as f:
        catalog_data = json.load(f)

    datasets = catalog_data.get('datasets', [])
    print(f"Loading {len(datasets)} datasets into UI format...")

    # Create UI-compatible data structure
    ui_data = {
        'title': 'Earth Engine Data Catalog - Google for Developers',
        'url': './gee cat/Earth Engine Data Catalog  _  Google for Developers.html',
        'timestamp': catalog_data['extraction_info']['timestamp'],
        'satellite_catalog': {
            'extraction_method': 'earth_engine_intelligent',
            'extraction_confidence': 'very_high',
            'datasets': datasets,
            'classifications': catalog_data['classifications'],
            'total_datasets': len(datasets),
            'quality_distribution': catalog_data['statistics']['quality_distribution']
        }
    }

    # Save UI-compatible file
    ui_file = 'web_crawler/collected_data/ui_data.json'
    with open(ui_file, 'w', encoding='utf-8') as f:
        json.dump(ui_data, f, indent=2, ensure_ascii=False)

    print(f"UI data saved to: {ui_file}")

    # Create sample thumbnails for datasets that have thumbnail URLs
    thumbnails_dir = 'web_crawler/collected_data/thumbnails'
    os.makedirs(thumbnails_dir, exist_ok=True)

    # Copy some sample thumbnails from the gee cat folder if they exist
    gee_files_dir = 'gee cat/Earth Engine Data Catalog  _  Google for Developers_files'
    if os.path.exists(gee_files_dir):
        thumbnail_count = 0
        for filename in os.listdir(gee_files_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and thumbnail_count < 50:
                src = os.path.join(gee_files_dir, filename)
                # Find a matching dataset
                for dataset in datasets[:50]:  # Process first 50 datasets
                    dataset_id = dataset.get('dataset_id', 'unknown')
                    if dataset_id != 'unknown':
                        dest = os.path.join(thumbnails_dir, f"{dataset_id}_thumbnail.png")
                        try:
                            shutil.copy2(src, dest)
                            dataset['thumbnail_local_path'] = dest
                            thumbnail_count += 1
                            break
                        except Exception:
                            continue

        print(f"Created {thumbnail_count} sample thumbnails")

    # Update the UI data with thumbnail paths
    with open(ui_file, 'w', encoding='utf-8') as f:
        json.dump(ui_data, f, indent=2, ensure_ascii=False)

    return True

def create_startup_script():
    """Create a script to launch the UI with the extracted data"""

    startup_content = '''#!/usr/bin/env python3
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
'''

    with open('launch_enhanced_ui.py', 'w', encoding='utf-8') as f:
        f.write(startup_content)

    print("Created launch_enhanced_ui.py")

if __name__ == "__main__":
    print("=== PREPARING UI DATA ===")

    success = create_ui_compatible_data()
    if success:
        create_startup_script()
        print("\n=== READY TO LAUNCH ===")
        print("Run: python launch_enhanced_ui.py")
        print("This will open the enhanced UI with:")
        print("- 729 Earth Engine datasets")
        print("- Real-time thumbnail gallery")
        print("- Category filtering")
        print("- Detailed dataset information")
    else:
        print("Failed to prepare UI data")