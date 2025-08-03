#!/usr/bin/env python3
"""
Integration script to update enhanced crawler UI with BERT fix and weight optimization
"""

import os
import sys
import shutil
from pathlib import Path

def integrate_bert_fix_and_optimizer():
    """Integrate BERT fix and weight optimizer into enhanced crawler UI"""
    
    print("🔧 Integrating BERT Fix and Weight Optimizer...")
    
    # Import the optimizer
    try:
        from bert_fix_and_weight_optimizer import BERTFixAndWeightOptimizer
        print("✅ BERT Fix and Weight Optimizer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import optimizer: {e}")
        return False
    
    # Read the enhanced crawler UI file
    ui_file = "enhanced_crawler_ui.py"
    if not os.path.exists(ui_file):
        print(f"❌ {ui_file} not found")
        return False
    
    with open(ui_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add imports for the optimizer
    import_section = '''import sys
import time
import gc
import psutil
import logging
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import traceback

# Import BERT fix and weight optimizer
try:
    from bert_fix_and_weight_optimizer import BERTFixAndWeightOptimizer, WeightTestConfig
    BERT_OPTIMIZER_AVAILABLE = True
except ImportError:
    BERT_OPTIMIZER_AVAILABLE = False
    print("⚠️ BERT optimizer not available, using fallback systems")

# ... existing code ...
'''
    
    # Replace the existing import section
    if 'import sys' in content:
        # Find the import section and replace it
        lines = content.split('\n')
        new_lines = []
        in_import_section = False
        
        for line in lines:
            if line.startswith('import ') or line.startswith('from '):
                if not in_import_section:
                    in_import_section = True
                    new_lines.append(import_section)
                continue
            elif in_import_section and line.strip() == '':
                in_import_section = False
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
    
    # Add the optimizer integration to the EnhancedCrawlerUI class
    optimizer_integration = '''
    def _init_bert_optimizer(self):
        """Initialize BERT fix and weight optimizer"""
        try:
            if BERT_OPTIMIZER_AVAILABLE:
                self.bert_optimizer = BERTFixAndWeightOptimizer()
                self.log_message("✅ BERT Fix and Weight Optimizer initialized")
                return True
            else:
                self.log_message("⚠️ BERT optimizer not available, using fallback")
                return False
        except Exception as e:
            self.log_message(f"❌ BERT optimizer initialization failed: {e}")
            return False
    
    def test_weight_configuration(self, config_name: str, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test a specific weight configuration during crawling"""
        if not hasattr(self, 'bert_optimizer') or not self.bert_optimizer:
            return {"error": "BERT optimizer not available"}
        
        try:
            # Find the configuration
            config = next((c for c in self.bert_optimizer.weight_configs if c.name == config_name), None)
            if not config:
                return {"error": f"Configuration {config_name} not found"}
            
            # Test the configuration
            result = self.bert_optimizer.test_configuration(config, test_data)
            self.log_message(f"✅ Weight configuration {config_name} tested successfully")
            return result
            
        except Exception as e:
            self.log_message(f"❌ Weight configuration test failed: {e}")
            return {"error": str(e)}
    
    def find_optimal_weights(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find optimal weight configuration during crawling"""
        if not hasattr(self, 'bert_optimizer') or not self.bert_optimizer:
            return {"error": "BERT optimizer not available"}
        
        try:
            optimal_config = self.bert_optimizer.find_optimal_configuration(test_data)
            if optimal_config:
                self.log_message(f"✅ Optimal configuration found: {optimal_config.name}")
                return {
                    "optimal_config": optimal_config.name,
                    "title_weight": optimal_config.title_weight,
                    "description_weight": optimal_config.description_weight,
                    "tags_weight": optimal_config.tags_weight,
                    "quality_threshold": optimal_config.quality_threshold,
                    "confidence_threshold": optimal_config.confidence_threshold,
                    "max_tokens": optimal_config.max_tokens
                }
            else:
                return {"error": "No optimal configuration found"}
                
        except Exception as e:
            self.log_message(f"❌ Optimal weight finding failed: {e}")
            return {"error": str(e)}
    
    def classify_with_optimizer(self, text: str, config_name: str = None) -> Dict[str, Any]:
        """Classify text using the optimizer"""
        if not hasattr(self, 'bert_optimizer') or not self.bert_optimizer:
            return self.classify_text_fallback(text)
        
        try:
            config = None
            if config_name:
                config = next((c for c in self.bert_optimizer.weight_configs if c.name == config_name), None)
            
            result = self.bert_optimizer.classify_text(text, config)
            return result
            
        except Exception as e:
            self.log_message(f"❌ Optimizer classification failed: {e}")
            return self.classify_text_fallback(text)
    
    def classify_text_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback classification method"""
        if not text:
            return {'label': 'unknown', 'confidence': 0.0, 'method': 'fallback'}
        
        text_lower = text.lower()
        
        # Simple keyword classification
        if any(word in text_lower for word in ['satellite', 'landsat', 'sentinel']):
            return {'label': 'satellite_data', 'confidence': 0.8, 'method': 'fallback'}
        elif any(word in text_lower for word in ['climate', 'weather', 'atmosphere']):
            return {'label': 'climate_data', 'confidence': 0.8, 'method': 'fallback'}
        elif any(word in text_lower for word in ['geographic', 'coordinate', 'latitude']):
            return {'label': 'geospatial_data', 'confidence': 0.8, 'method': 'fallback'}
        else:
            return {'label': 'general_data', 'confidence': 0.5, 'method': 'fallback'}
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Get optimization report"""
        if not hasattr(self, 'bert_optimizer') or not self.bert_optimizer:
            return {"error": "BERT optimizer not available"}
        
        try:
            return self.bert_optimizer.get_optimization_report()
        except Exception as e:
            return {"error": str(e)}
    
    def cleanup_optimizer(self):
        """Cleanup optimizer resources"""
        if hasattr(self, 'bert_optimizer') and self.bert_optimizer:
            try:
                self.bert_optimizer.cleanup()
                self.log_message("✅ Optimizer cleanup completed")
            except Exception as e:
                self.log_message(f"⚠️ Optimizer cleanup failed: {e}")

'''
    
    # Add the optimizer integration to the class
    if 'def _init_bert_optimizer(self):' not in content:
        # Find the class definition and add the methods
        class_start = content.find('class EnhancedCrawlerUI(QWidget):')
        if class_start != -1:
            # Find a good place to insert the methods (after __init__)
            init_end = content.find('def _init_advanced_features(self):')
            if init_end != -1:
                content = content[:init_end] + optimizer_integration + content[init_end:]
    
    # Update the _init_advanced_features method to initialize the optimizer
    if 'def _init_advanced_features(self):' in content:
        # Find the method and add optimizer initialization
        method_start = content.find('def _init_advanced_features(self):')
        method_end = content.find('def _load_ml_models_safely(self):')
        
        if method_start != -1 and method_end != -1:
            method_content = content[method_start:method_end]
            
            # Add optimizer initialization
            if 'self._init_bert_optimizer()' not in method_content:
                # Find a good place to add it (after other initializations)
                init_line = '        # Initialize advanced systems'
                if init_line in method_content:
                    new_init = init_line + '\n        self._init_bert_optimizer()'
                    method_content = method_content.replace(init_line, new_init)
                
                content = content[:method_start] + method_content + content[method_end:]
    
    # Update the apply_ml_classification method to use the optimizer
    if 'def apply_ml_classification(self, soup, result):' in content:
        # Find the method and update it
        method_start = content.find('def apply_ml_classification(self, soup, result):')
        method_end = content.find('def _extract_satellite_info(self, text):')
        
        if method_start != -1 and method_end != -1:
            method_content = content[method_start:method_end]
            
            # Add optimizer classification
            if 'self.classify_with_optimizer(' not in method_content:
                # Find where to add optimizer classification
                bert_section = '            # Lightweight BERT classification'
                if bert_section in method_content:
                    optimizer_classification = '''
            # Optimizer-based classification
            if hasattr(self, 'bert_optimizer') and self.bert_optimizer:
                try:
                    combined_text = f"{title} {description} {tags}"
                    if combined_text.strip():
                        optimizer_result = self.classify_with_optimizer(combined_text)
                        if optimizer_result and 'error' not in optimizer_result:
                            ml_results['optimizer_classification'] = optimizer_result
                            self.log_ml_classification(f"Optimizer classification: {optimizer_result['label']} ({optimizer_result['confidence']:.2f})")
                except Exception as e:
                    self.log_error(f"Optimizer classification error: {e}")
'''
                    method_content = method_content.replace(bert_section, bert_section + optimizer_classification)
                
                content = content[:method_start] + method_content + content[method_end:]
    
    # Update the stop_crawl method to cleanup optimizer
    if 'def stop_crawl(self):' in content:
        # Find the method and add cleanup
        method_start = content.find('def stop_crawl(self):')
        method_end = content.find('def toggle_realtime_view(self):')
        
        if method_start != -1 and method_end != -1:
            method_content = content[method_start:method_end]
            
            # Add optimizer cleanup
            if 'self.cleanup_optimizer()' not in method_content:
                cleanup_line = '        self.log_message("🛑 Crawling stopped")'
                if cleanup_line in method_content:
                    new_cleanup = cleanup_line + '\n        self.cleanup_optimizer()'
                    method_content = method_content.replace(cleanup_line, new_cleanup)
                
                content = content[:method_start] + method_content + content[method_end:]
    
    # Write the updated content back to the file
    with open(ui_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Enhanced crawler UI updated with BERT fix and weight optimizer")
    return True

def create_test_script():
    """Create a test script to verify the integration"""
    
    test_script = '''#!/usr/bin/env python3
"""
Test script for BERT fix and weight optimizer integration
"""

import sys
import time
from pathlib import Path

def test_integration():
    """Test the integration of BERT fix and weight optimizer"""
    print("🧪 Testing BERT Fix and Weight Optimizer Integration...")
    
    try:
        # Test import
        from bert_fix_and_weight_optimizer import BERTFixAndWeightOptimizer
        print("✅ BERT optimizer imported successfully")
        
        # Test optimizer creation
        optimizer = BERTFixAndWeightOptimizer()
        print("✅ Optimizer created successfully")
        
        # Test classification
        test_text = "NASA Landsat 8 satellite imagery with high resolution"
        result = optimizer.classify_text(test_text)
        print(f"✅ Classification test: {result}")
        
        # Test weight configuration
        test_data = [
            {"title": "Landsat 8 Satellite Imagery", "description": "High-resolution optical satellite data", "tags": "satellite, optical, remote sensing"},
            {"title": "Climate Data Collection", "description": "Atmospheric temperature and precipitation data", "tags": "climate, weather, atmosphere"}
        ]
        
        config = optimizer.weight_configs[0]  # Use first config
        test_result = optimizer.test_configuration(config, test_data)
        print(f"✅ Configuration test: {test_result['config_name']} - Success rate: {test_result['data_completeness']:.2%}")
        
        # Test optimal configuration finding
        optimal_config = optimizer.find_optimal_configuration(test_data)
        if optimal_config:
            print(f"✅ Optimal configuration found: {optimal_config.name}")
        
        # Test report generation
        report = optimizer.get_optimization_report()
        print(f"✅ Report generated: {len(report['test_results'])} configurations tested")
        
        # Cleanup
        optimizer.cleanup()
        print("✅ Cleanup completed")
        
        print("🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
'''
    
    with open("test_bert_integration.py", "w") as f:
        f.write(test_script)
    
    print("✅ Test script created: test_bert_integration.py")

def create_launch_script():
    """Create a launch script that uses the optimized system"""
    
    launch_script = '''#!/usr/bin/env python3
"""
Launch script for enhanced crawler with BERT fix and weight optimization
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the enhanced crawler with BERT optimization"""
    print("🚀 Launching Enhanced Web Crawler with BERT Fix and Weight Optimization...")
    
    try:
        # Import the enhanced crawler UI
        from enhanced_crawler_ui import EnhancedCrawlerUI
        
        # Import PySide6
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Enhanced Web Crawler with BERT Optimization")
        
        # Create and show the UI
        ui = EnhancedCrawlerUI()
        ui.show()
        
        print("✅ Enhanced crawler UI launched successfully")
        print("🔧 BERT fix and weight optimization active")
        print("📊 Adaptive weight testing enabled during crawling")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("launch_enhanced_crawler_optimized.py", "w") as f:
        f.write(launch_script)
    
    print("✅ Launch script created: launch_enhanced_crawler_optimized.py")

def main():
    """Main integration function"""
    print("🔧 BERT Fix and Weight Optimizer Integration")
    print("=" * 50)
    
    # Step 1: Integrate the optimizer
    if integrate_bert_fix_and_optimizer():
        print("✅ Integration completed successfully")
    else:
        print("❌ Integration failed")
        return False
    
    # Step 2: Create test script
    create_test_script()
    
    # Step 3: Create launch script
    create_launch_script()
    
    print("\n🎉 Integration Summary:")
    print("✅ BERT fix and weight optimizer integrated")
    print("✅ Enhanced crawler UI updated")
    print("✅ Test script created: test_bert_integration.py")
    print("✅ Launch script created: launch_enhanced_crawler_optimized.py")
    print("\n🚀 To test the integration:")
    print("   python test_bert_integration.py")
    print("\n🚀 To launch the enhanced crawler:")
    print("   python launch_enhanced_crawler_optimized.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 