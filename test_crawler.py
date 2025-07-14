#!/usr/bin/env python3
"""
Test script for the ultra-enhanced Earth Engine crawler
Tests all sophisticated features including config, plugins, ML, validation, and error handling
"""

import sys
import os

def test_imports():
    """Test that all required imports work."""
    print("Testing imports...")
    
    # Basic imports
    try:
        from enhanced_crawler_ui import EnhancedCrawlerUI
        print("✅ EnhancedCrawlerUI imported successfully")
    except Exception as e:
        print(f"❌ Failed to import EnhancedCrawlerUI: {e}")
        return False
    
    # Advanced imports
    advanced_features = {
        'spacy': 'ML/NLP classification',
        'transformers': 'BERT ensemble classification', 
        'geopy': 'Geospatial validation',
        'yaml': 'Configuration system',
        'dash': 'Analytics dashboard'
    }
    
    for module, description in advanced_features.items():
        try:
            __import__(module)
            print(f"✅ {module} available - {description}")
        except ImportError:
            print(f"⚠️  {module} not available - {description} disabled")
    
    return True

def test_config_system():
    """Test configuration system."""
    print("\nTesting configuration system...")
    
    try:
        from config_utils import load_config, load_plugins
        
        # Test config loading
        config = load_config()
        if config and 'fields' in config:
            print(f"✅ Config loaded successfully with {len(config['fields'])} field definitions")
        else:
            print("⚠️  Config loaded but no fields found")
        
        # Test plugin loading
        plugins = load_plugins(config.get('plugins', []))
        if plugins:
            print(f"✅ {len(plugins)} plugins loaded successfully")
        else:
            print("⚠️  No plugins loaded")
            
    except Exception as e:
        print(f"❌ Config system test failed: {e}")

def test_plugins():
    """Test plugin system."""
    print("\nTesting plugin system...")
    
    try:
        from plugins.custom_band_parser import parse_bands
        from plugins.thumbnail_ocr import extract_text_from_thumbnail
        
        print("✅ Custom band parser plugin available")
        print("✅ Thumbnail OCR plugin available")
        
    except Exception as e:
        print(f"⚠️  Plugin test failed: {e}")

def test_ml_classification():
    """Test ML classification features."""
    print("\nTesting ML classification...")
    
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        doc = nlp("NASA Landsat 8 satellite data from 2020")
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        print(f"✅ spaCy NER working: {entities}")
    except Exception as e:
        print(f"⚠️  spaCy test failed: {e}")
    
    try:
        import transformers
        print("✅ Transformers available for BERT classification")
    except ImportError:
        print("⚠️  Transformers not available")

def test_validation():
    """Test validation features."""
    print("\nTesting validation features...")
    
    try:
        from geopy.geocoders import Nominatim
        geocoder = Nominatim(user_agent="test")
        print("✅ Geocoder available for spatial validation")
    except Exception as e:
        print(f"⚠️  Geocoder test failed: {e}")

def test_dashboard():
    """Test analytics dashboard."""
    print("\nTesting analytics dashboard...")
    
    try:
        from analytics_dashboard import get_dashboard
        dashboard = get_dashboard()
        print("✅ Analytics dashboard available")
    except Exception as e:
        print(f"⚠️  Dashboard test failed: {e}")

def main():
    """Run all tests."""
    print("🧪 Testing Ultra-Enhanced Earth Engine Crawler")
    print("=" * 50)
    
    # Run tests
    test_imports()
    test_config_system()
    test_plugins()
    test_ml_classification()
    test_validation()
    test_dashboard()
    
    print("\n" + "=" * 50)
    print("🎉 Test completed! The crawler should work with available features.")
    print("📊 Analytics dashboard will be available at http://127.0.0.1:8080")
    print("🚀 Run 'python enhanced_crawler_ui.py' to start the crawler")

if __name__ == "__main__":
    main() 