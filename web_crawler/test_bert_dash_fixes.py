#!/usr/bin/env python3
"""
Test script to verify BERT and Dash integration fixes
"""

import sys
import os
import time
import threading
import subprocess

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing package imports...")
    
    # Test basic imports
    try:
        import spacy
        print("✓ spaCy imported successfully")
    except ImportError:
        print("⚠ spaCy not available")
    
    try:
        import transformers
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        print("✓ Transformers imported successfully")
    except ImportError:
        print("⚠ Transformers not available")
    
    try:
        import dash
        import plotly
        print("✓ Dash and Plotly imported successfully")
    except ImportError:
        print("⚠ Dash/Plotly not available")
    
    try:
        import sklearn
        print("✓ Scikit-learn imported successfully")
    except ImportError:
        print("⚠ Scikit-learn not available")

def test_dashboard():
    """Test dashboard creation and functionality"""
    print("\nTesting dashboard functionality...")
    
    try:
        from analytics_dashboard import AnalyticsDashboard
        
        # Create dashboard
        dashboard = AnalyticsDashboard(port=8081)  # Use different port for testing
        print("✓ Dashboard created successfully")
        
        # Test data addition
        test_data = {
            'title': 'Test Dataset',
            'provider': 'NASA',
            'confidence': {'title': 0.9, 'description': 0.8},
            'tags': ['satellite', 'landsat'],
            'ml_classification': {'bert': {'label': 'satellite_data', 'confidence': 0.85}}
        }
        
        dashboard.add_data(test_data)
        print("✓ Data added to dashboard successfully")
        
        # Test batch data addition
        batch_data = [
            {'title': 'Dataset 1', 'provider': 'ESA', 'confidence': {'title': 0.95}},
            {'title': 'Dataset 2', 'provider': 'USGS', 'confidence': {'title': 0.88}}
        ]
        dashboard.add_batch_data(batch_data)
        print("✓ Batch data added to dashboard successfully")
        
        # Test data retrieval
        data = dashboard.get_data()
        print(f"✓ Retrieved {len(data)} items from dashboard")
        
        return True
        
    except Exception as e:
        print(f"✗ Dashboard test failed: {e}")
        return False

def test_bert_loading():
    """Test BERT model loading"""
    print("\nTesting BERT model loading...")
    
    try:
        import transformers
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        # Test lightweight model loading
        model_name = "distilbert-base-uncased"
        
        print("Loading DistilBERT tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("✓ Tokenizer loaded successfully")
        
        print("Loading DistilBERT model...")
        model = AutoModelForSequenceClassification.from_pretrained(
            model_name, 
            num_labels=5
        )
        print("✓ Model loaded successfully")
        
        # Test simple classification
        from transformers import pipeline
        classifier = pipeline(
            "text-classification", 
            model=model, 
            tokenizer=tokenizer,
            device=-1
        )
        
        test_text = "NASA Landsat satellite data"
        result = classifier(test_text, truncation=True, max_length=128)
        print(f"✓ Classification test successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"✗ BERT test failed: {e}")
        return False

def test_crawler_integration():
    """Test crawler integration"""
    print("\nTesting crawler integration...")
    
    try:
        # Import the crawler class
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        # Create a minimal test instance
        print("Creating crawler instance...")
        # Note: This will create a Qt application, so we need to be careful
        # For testing, we'll just check if the class can be imported and instantiated
        
        print("✓ Crawler class imported successfully")
        
        # Test the simple classification method
        crawler = EnhancedCrawlerUI()
        
        # Test simple classification
        test_text = "Landsat 8 satellite imagery from NASA"
        classification = crawler.simple_classify_text(test_text)
        print(f"✓ Simple classification test: {classification}")
        
        return True
        
    except Exception as e:
        print(f"✗ Crawler integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== BERT and Dash Integration Test Suite ===\n")
    
    # Test imports
    test_imports()
    
    # Test dashboard
    dashboard_ok = test_dashboard()
    
    # Test BERT
    bert_ok = test_bert_loading()
    
    # Test crawler integration
    crawler_ok = test_crawler_integration()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Dashboard: {'✓ PASS' if dashboard_ok else '✗ FAIL'}")
    print(f"BERT: {'✓ PASS' if bert_ok else '✗ FAIL'}")
    print(f"Crawler Integration: {'✓ PASS' if crawler_ok else '✗ FAIL'}")
    
    if dashboard_ok and bert_ok and crawler_ok:
        print("\n🎉 All tests passed! BERT and Dash integration is working correctly.")
        return 0
    else:
        print("\n⚠ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 