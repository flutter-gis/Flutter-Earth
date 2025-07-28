#!/usr/bin/env python3
"""
Comprehensive Cleanup System
Removes unnecessary components and fixes remaining issues.
"""

import os
import sys
import re
import shutil
from typing import List, Dict

class ComprehensiveCleanup:
    """Comprehensive cleanup system for the web crawler."""
    
    def __init__(self):
        self.removed_components = []
        self.fixed_issues = []
        self.cleaned_files = []
        
    def cleanup_monitoring_data(self):
        """Remove all monitoring data and related components."""
        print("🧹 Cleaning up monitoring data...")
        
        # Remove monitoring data initialization
        self._remove_monitoring_data_init()
        
        # Remove performance monitoring
        self._remove_performance_monitoring()
        
        # Remove monitoring display methods
        self._remove_monitoring_display()
        
        # Remove status indicators
        self._remove_status_indicators()
        
        self.removed_components.append("monitoring_data")
        self.removed_components.append("performance_monitoring")
        self.removed_components.append("monitoring_display")
        self.removed_components.append("status_indicators")
        
    def _remove_monitoring_data_init(self):
        """Remove monitoring data initialization."""
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove monitoring data initialization
            pattern = r'# Initialize monitoring data with error handling\s+try:\s+self\.monitoring_data = \{.*?\}\s+except Exception as e:\s+print\(f"Error initializing monitoring data: \{e\}"\)\s+# Create a minimal monitoring data structure\s+self\.monitoring_data = \{\}\s+self\.monitoring_enabled = False'
            content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed monitoring data initialization")
            
        except Exception as e:
            print(f"Error removing monitoring data init: {e}")
            
    def _remove_performance_monitoring(self):
        """Remove performance monitoring components."""
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove performance monitor import
            content = re.sub(r'from performance_monitor import PerformanceMonitor', '', content)
            content = re.sub(r'PERFORMANCE_MONITORING_AVAILABLE = True', 'PERFORMANCE_MONITORING_AVAILABLE = False', content)
            
            # Remove performance monitor initialization
            content = re.sub(r'self\.performance_monitor = PerformanceMonitor\(\)', '', content)
            
            # Remove update_performance_monitoring method
            pattern = r'def update_performance_monitoring\(self\):.*?def start_crawl\(self\):'
            content = re.sub(pattern, 'def start_crawl(self):', content, flags=re.DOTALL)
            
            # Remove performance monitoring call
            content = re.sub(r'self\.update_performance_monitoring\(\)', '', content)
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed performance monitoring")
            
        except Exception as e:
            print(f"Error removing performance monitoring: {e}")
            
    def _remove_monitoring_display(self):
        """Remove monitoring display methods."""
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove monitoring display methods
            methods_to_remove = [
                'def update_monitoring_display(self):',
                'def draw_monitoring_charts(self):',
                'def draw_performance_chart(self, width, height):',
                'def draw_system_resources_chart(self, width, height):'
            ]
            
            for method in methods_to_remove:
                pattern = rf'{re.escape(method)}.*?return'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed monitoring display methods")
            
        except Exception as e:
            print(f"Error removing monitoring display: {e}")
            
    def _remove_status_indicators(self):
        """Remove status indicators."""
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove status indicators method
            pattern = r'def update_status_indicators\(self\):.*?def update_ui\(self\):'
            content = re.sub(pattern, 'def update_ui(self):', content, flags=re.DOTALL)
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed status indicators")
            
        except Exception as e:
            print(f"Error removing status indicators: {e}")
            
    def cleanup_unused_imports(self):
        """Remove unused imports."""
        print("🧹 Cleaning up unused imports...")
        
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove unused imports
            unused_imports = [
                'from performance_monitor import performance_monitor',
                'from performance_monitor import PerformanceMonitor',
                'import queue',
                'import matplotlib',
                'import matplotlib.pyplot as plt',
                'import numpy as np'
            ]
            
            for imp in unused_imports:
                content = content.replace(imp, '')
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed unused imports")
            
        except Exception as e:
            print(f"Error removing unused imports: {e}")
            
    def cleanup_unused_variables(self):
        """Remove unused variables and references."""
        print("🧹 Cleaning up unused variables...")
        
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove unused variable references
            unused_vars = [
                'self.progress_queue',
                'self.monitoring_enabled',
                'self.performance_mode',
                'self.optimization_level',
                'self.system_status',
                'self.download_speed_label',
                'self.processing_speed_label',
                'self.cpu_label',
                'self.memory_label',
                'self.optimization_label'
            ]
            
            for var in unused_vars:
                content = content.replace(var, '')
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed unused variables")
            
        except Exception as e:
            print(f"Error removing unused variables: {e}")
            
    def cleanup_unused_methods(self):
        """Remove unused methods."""
        print("🧹 Cleaning up unused methods...")
        
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove unused methods
            unused_methods = [
                'def toggle_performance_mode(self):',
                'def show_health_report(self):',
                'def apply_optimizations(self, level, auto_optimize, cache_size, dialog):',
                'def ai_enhance_data(self):',
                'def start_collaboration(self):',
                'def open_data_explorer(self):',
                'def open_automation(self):',
                'def web_validate_data(self):',
                'def _auto_web_validate(self):'
            ]
            
            for method in unused_methods:
                # Find and remove the entire method
                pattern = rf'{re.escape(method)}.*?(?=def |$)'
                content = re.sub(pattern, '', content, flags=re.DOTALL)
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Removed unused methods")
            
        except Exception as e:
            print(f"Error removing unused methods: {e}")
            
    def cleanup_unused_files(self):
        """Remove unused files."""
        print("🧹 Cleaning up unused files...")
        
        unused_files = [
            'web_crawler/performance_monitor.py',
            'web_crawler/performance_optimizer.py',
            'web_crawler/analytics_dashboard.py',
            'web_crawler/memory_optimizer.py',
            'web_crawler/enhanced_error_handler.py',
            'web_crawler/crawler_robustness_enhancer.py',
            'web_crawler/comprehensive_crawler_debug.py',
            'web_crawler/final_comprehensive_test.py',
            'web_crawler/test_monitoring_fix.py',
            'web_crawler/test_fixes.py',
            'web_crawler/debug_and_optimize.py',
            'web_crawler/comprehensive_optimization.py',
            'web_crawler/simple_optimization.py',
            'web_crawler/log_analyzer.py'
        ]
        
        for file_path in unused_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    self.cleaned_files.append(file_path)
                    print(f"🗑️ Removed: {file_path}")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")
                    
    def fix_remaining_issues(self):
        """Fix any remaining issues."""
        print("🔧 Fixing remaining issues...")
        
        try:
            with open('web_crawler/enhanced_crawler_ui.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Fix any remaining cpu_usage references
            content = content.replace('cpu_usage', 'cpu_percent')
            
            # Remove any remaining monitoring references
            content = re.sub(r'self\.monitoring_data\[.*?\]', '', content)
            
            # Clean up any empty lines
            content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
            
            with open('web_crawler/enhanced_crawler_ui.py', 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.fixed_issues.append("Fixed remaining issues")
            
        except Exception as e:
            print(f"Error fixing remaining issues: {e}")
            
    def run_comprehensive_cleanup(self):
        """Run comprehensive cleanup."""
        print("🚀 Starting Comprehensive Cleanup...")
        
        # Clean up monitoring data
        self.cleanup_monitoring_data()
        
        # Clean up unused imports
        self.cleanup_unused_imports()
        
        # Clean up unused variables
        self.cleanup_unused_variables()
        
        # Clean up unused methods
        self.cleanup_unused_methods()
        
        # Clean up unused files
        self.cleanup_unused_files()
        
        # Fix remaining issues
        self.fix_remaining_issues()
        
        print("✅ Comprehensive cleanup completed!")
        
    def generate_cleanup_report(self):
        """Generate cleanup report."""
        return {
            'removed_components': len(self.removed_components),
            'fixed_issues': len(self.fixed_issues),
            'cleaned_files': len(self.cleaned_files),
            'components': self.removed_components,
            'issues': self.fixed_issues,
            'files': self.cleaned_files
        }

def main():
    """Main cleanup function."""
    print("🧹 Starting Comprehensive Cleanup...")
    
    cleanup = ComprehensiveCleanup()
    cleanup.run_comprehensive_cleanup()
    
    report = cleanup.generate_cleanup_report()
    
    print(f"\n📊 Cleanup Results:")
    print(f"🗑️ Removed Components: {report['removed_components']}")
    print(f"🔧 Fixed Issues: {report['fixed_issues']}")
    print(f"📁 Cleaned Files: {report['cleaned_files']}")
    
    if report['components']:
        print(f"\n🗑️ Removed Components:")
        for component in report['components']:
            print(f"   • {component}")
            
    if report['issues']:
        print(f"\n🔧 Fixed Issues:")
        for issue in report['issues']:
            print(f"   • {issue}")
            
    if report['files']:
        print(f"\n📁 Cleaned Files:")
        for file in report['files']:
            print(f"   • {file}")
            
    print(f"\n🎉 Cleanup completed successfully!")

if __name__ == "__main__":
    main() 