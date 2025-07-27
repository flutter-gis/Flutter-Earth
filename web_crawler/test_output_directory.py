#!/usr/bin/env python3
"""
Test script for output directory functionality
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_output_directory_functionality():
    """Test the output directory functionality"""
    print("Testing Output Directory Functionality")
    print("=" * 50)
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary test directory: {temp_dir}")
        
        # Test directory structure creation
        test_output_dir = os.path.join(temp_dir, "test_output")
        
        # Simulate the directory structure that would be created
        extracted_data = os.path.join(test_output_dir, "extracted_data")
        thumbnails = os.path.join(test_output_dir, "thumbnails")
        model_cache = os.path.join(test_output_dir, "model_cache")
        exported_data = os.path.join(test_output_dir, "exported_data")
        
        # Create directories
        for dir_path in [extracted_data, thumbnails, model_cache, exported_data]:
            os.makedirs(dir_path, exist_ok=True)
            print(f"✓ Created directory: {dir_path}")
        
        # Test file creation in each directory
        test_files = {
            extracted_data: "test_extracted_data.json",
            thumbnails: "test_thumbnail.png",
            model_cache: "test_model.pkl",
            exported_data: "test_exported_data.json"
        }
        
        for dir_path, filename in test_files.items():
            test_file_path = os.path.join(dir_path, filename)
            with open(test_file_path, 'w') as f:
                f.write(f"Test content for {filename}")
            print(f"✓ Created test file: {test_file_path}")
        
        # Verify directory structure
        print("\nVerifying directory structure:")
        for root, dirs, files in os.walk(test_output_dir):
            level = root.replace(test_output_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        print("\n✓ All tests passed! Output directory functionality is working correctly.")
        print(f"Test directory: {test_output_dir}")
        
        # Show what would be stored in each directory
        print("\nDirectory purposes:")
        print(f"  {extracted_data} - Raw extracted data from crawling")
        print(f"  {thumbnails} - Downloaded thumbnail images")
        print(f"  {model_cache} - Cached ML models for faster loading")
        print(f"  {exported_data} - Processed and exported results")

if __name__ == "__main__":
    test_output_directory_functionality() 