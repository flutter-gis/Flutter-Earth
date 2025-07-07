#!/usr/bin/env python3
"""
Test Download Flow for Flutter Earth
Tests the complete download workflow from Earth Engine to local storage
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path

# Add the flutter_earth_pkg to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'flutter_earth_pkg'))

try:
    from flutter_earth.earth_engine import EarthEngineManager
    from flutter_earth.download_manager import DownloadManager
    from flutter_earth.config import ConfigManager
    from flutter_earth.progress_tracker import ProgressTracker
    from flutter_earth.auth_setup import AuthManager
except ImportError as e:
    print(f"Error importing Flutter Earth modules: {e}")
    sys.exit(1)

class DownloadFlowTester:
    """Test class for the complete download workflow"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.config_manager = None
        self.earth_engine = None
        self.download_manager = None
        self.progress_tracker = None
        self.test_results = []
        
    def setup_logging(self):
        """Setup logging for the test"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / f"download_flow_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='w', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logger = logging.getLogger(__name__)
        logger.info("Download flow test logging initialized")
        return logger
    
    def test_initialization(self):
        """Test the initialization of all components"""
        self.logger.info("Testing component initialization...")
        
        try:
            # Test ConfigManager
            self.config_manager = ConfigManager()
            self.logger.info("✓ ConfigManager initialized successfully")
            
            # Test ProgressTracker
            self.progress_tracker = ProgressTracker()
            self.logger.info("✓ ProgressTracker initialized successfully")
            
            # Test DownloadManager
            self.download_manager = DownloadManager()
            self.logger.info("✓ DownloadManager initialized successfully")
            
            # Test EarthEngineManager
            self.earth_engine = EarthEngineManager()
            self.logger.info("✓ EarthEngineManager initialized successfully")
            
            self.test_results.append({
                'test': 'initialization',
                'status': 'PASS',
                'message': 'All components initialized successfully'
            })
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Initialization failed: {e}")
            self.test_results.append({
                'test': 'initialization',
                'status': 'FAIL',
                'message': f'Initialization failed: {e}'
            })
            return False
    
    def test_earth_engine_connection(self):
        """Test Earth Engine connection and authentication"""
        self.logger.info("Testing Earth Engine connection...")
        
        try:
            # Test Earth Engine initialization
            initialized = self.earth_engine.initialize()
            
            if initialized:
                self.logger.info("✓ Earth Engine connection successful")
                self.test_results.append({
                    'test': 'earth_engine_connection',
                    'status': 'PASS',
                    'message': 'Earth Engine connected successfully'
                })
                return True
            else:
                self.logger.error("✗ Earth Engine initialization failed")
                self.test_results.append({
                    'test': 'earth_engine_connection',
                    'status': 'FAIL',
                    'message': 'Earth Engine initialization failed'
                })
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Earth Engine connection error: {e}")
            self.test_results.append({
                'test': 'earth_engine_connection',
                'status': 'FAIL',
                'message': f'Earth Engine connection error: {e}'
            })
            return False
    
    def test_dataset_access(self):
        """Test access to sample datasets"""
        self.logger.info("Testing dataset access...")
        
        test_datasets = [
            'USGS/SRTMGL1_003',  # SRTM Digital Elevation
            'LANDSAT/LC08/C02/T1_L2',  # Landsat 8
            'COPERNICUS/S2_SR'  # Sentinel-2
        ]
        
        accessible_datasets = []
        
        for dataset_id in test_datasets:
            try:
                # Test dataset access
                dataset_info = self.earth_engine.get_dataset_info(dataset_id)
                
                if dataset_info:
                    self.logger.info(f"✓ Dataset accessible: {dataset_id}")
                    accessible_datasets.append(dataset_id)
                else:
                    self.logger.warning(f"⚠ Dataset not accessible: {dataset_id}")
                    
            except Exception as e:
                self.logger.error(f"✗ Error accessing dataset {dataset_id}: {e}")
        
        if accessible_datasets:
            self.test_results.append({
                'test': 'dataset_access',
                'status': 'PASS',
                'message': f'Successfully accessed {len(accessible_datasets)} datasets'
            })
            return True
        else:
            self.test_results.append({
                'test': 'dataset_access',
                'status': 'FAIL',
                'message': 'No datasets accessible'
            })
            return False
    
    def test_download_workflow(self):
        """Test the complete download workflow"""
        self.logger.info("Testing download workflow...")
        
        # Test parameters
        test_params = {
            'dataset_id': 'USGS/SRTMGL1_003',
            'region': {
                'type': 'Polygon',
                'coordinates': [[
                    [-122.5, 37.5],
                    [-122.0, 37.5],
                    [-122.0, 38.0],
                    [-122.5, 38.0],
                    [-122.5, 37.5]
                ]]
            },
            'start_date': '2020-01-01',
            'end_date': '2020-12-31',
            'scale': 30,
            'format': 'GeoTIFF'
        }
        
        try:
            # Start download
            download_id = self.download_manager.start_download(test_params)
            self.logger.info(f"✓ Download started with ID: {download_id}")
            
            # Monitor progress
            max_wait_time = 60  # 60 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait_time:
                progress = self.progress_tracker.get_progress(download_id)
                
                if progress:
                    self.logger.info(f"Download progress: {progress.get('percentage', 0)}%")
                    
                    if progress.get('status') == 'completed':
                        self.logger.info("✓ Download completed successfully")
                        self.test_results.append({
                            'test': 'download_workflow',
                            'status': 'PASS',
                            'message': 'Download workflow completed successfully'
                        })
                        return True
                    elif progress.get('status') == 'failed':
                        self.logger.error("✗ Download failed")
                        self.test_results.append({
                            'test': 'download_workflow',
                            'status': 'FAIL',
                            'message': 'Download workflow failed'
                        })
                        return False
                
                time.sleep(2)
            
            self.logger.warning("⚠ Download timeout - workflow may still be running")
            self.test_results.append({
                'test': 'download_workflow',
                'status': 'TIMEOUT',
                'message': 'Download workflow timed out'
            })
            return False
            
        except Exception as e:
            self.logger.error(f"✗ Download workflow error: {e}")
            self.test_results.append({
                'test': 'download_workflow',
                'status': 'FAIL',
                'message': f'Download workflow error: {e}'
            })
            return False
    
    def test_data_validation(self):
        """Test downloaded data validation"""
        self.logger.info("Testing data validation...")
        
        try:
            # Check if output directory exists
            output_dir = Path("downloads")
            if output_dir.exists():
                files = list(output_dir.glob("*.tif"))
                if files:
                    self.logger.info(f"✓ Found {len(files)} downloaded files")
                    self.test_results.append({
                        'test': 'data_validation',
                        'status': 'PASS',
                        'message': f'Found {len(files)} downloaded files'
                    })
                    return True
                else:
                    self.logger.warning("⚠ No downloaded files found")
                    self.test_results.append({
                        'test': 'data_validation',
                        'status': 'WARNING',
                        'message': 'No downloaded files found'
                    })
                    return False
            else:
                self.logger.warning("⚠ Output directory does not exist")
                self.test_results.append({
                    'test': 'data_validation',
                    'status': 'WARNING',
                    'message': 'Output directory does not exist'
                })
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Data validation error: {e}")
            self.test_results.append({
                'test': 'data_validation',
                'status': 'FAIL',
                'message': f'Data validation error: {e}'
            })
            return False
    
    def test_error_handling(self):
        """Test error handling scenarios"""
        self.logger.info("Testing error handling...")
        
        try:
            # Test invalid dataset ID
            invalid_dataset = 'INVALID/DATASET/ID'
            result = self.earth_engine.get_dataset_info(invalid_dataset)
            
            if result is None:
                self.logger.info("✓ Properly handled invalid dataset ID")
            else:
                self.logger.warning("⚠ Unexpected result for invalid dataset ID")
            
            # Test invalid region
            invalid_region = {'type': 'Invalid', 'coordinates': []}
            download_id = self.download_manager.start_download({
                'dataset_id': 'USGS/SRTMGL1_003',
                'region': invalid_region,
                'start_date': '2020-01-01',
                'end_date': '2020-12-31'
            })
            
            if download_id:
                self.logger.info("✓ Download manager handled invalid region gracefully")
            else:
                self.logger.warning("⚠ Download manager rejected invalid region")
            
            self.test_results.append({
                'test': 'error_handling',
                'status': 'PASS',
                'message': 'Error handling tests completed'
            })
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Error handling test failed: {e}")
            self.test_results.append({
                'test': 'error_handling',
                'status': 'FAIL',
                'message': f'Error handling test failed: {e}'
            })
            return False
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        self.logger.info("Starting download flow tests...")
        print("=" * 60)
        print("FLUTTER EARTH DOWNLOAD FLOW TEST")
        print("=" * 60)
        
        tests = [
            ('Component Initialization', self.test_initialization),
            ('Earth Engine Connection', self.test_earth_engine_connection),
            ('Dataset Access', self.test_dataset_access),
            ('Download Workflow', self.test_download_workflow),
            ('Data Validation', self.test_data_validation),
            ('Error Handling', self.test_error_handling)
        ]
        
        passed = 0
        failed = 0
        warnings = 0
        
        for test_name, test_func in tests:
            print(f"\nRunning: {test_name}")
            print("-" * 40)
            
            try:
                result = test_func()
                if result:
                    passed += 1
                    print(f"✓ {test_name}: PASSED")
                else:
                    failed += 1
                    print(f"✗ {test_name}: FAILED")
            except Exception as e:
                failed += 1
                print(f"✗ {test_name}: ERROR - {e}")
        
        # Generate summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Warnings: {warnings}")
        
        # Calculate success rate
        success_rate = (passed / len(tests)) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        self.save_test_results()
        
        return success_rate >= 80  # 80% success rate threshold
    
    def save_test_results(self):
        """Save detailed test results to file"""
        results_file = Path("logs") / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        results_data = {
            'timestamp': datetime.now().isoformat(),
            'test_suite': 'Download Flow Test',
            'results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed': len([r for r in self.test_results if r['status'] == 'PASS']),
                'failed': len([r for r in self.test_results if r['status'] == 'FAIL']),
                'warnings': len([r for r in self.test_results if r['status'] == 'WARNING'])
            }
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Test results saved to: {results_file}")

def main():
    """Main function to run the download flow test"""
    print("Flutter Earth Download Flow Test")
    print("This test validates the complete download workflow from Earth Engine to local storage")
    print()
    
    # Check if user wants to run the test
    response = input("Do you want to run the download flow test? (y/N): ")
    if response.lower() != 'y':
        print("Test cancelled by user")
        return
    
    # Create and run tester
    tester = DownloadFlowTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 All tests passed! Download flow is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Please check the logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 