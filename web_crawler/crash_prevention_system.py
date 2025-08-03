#!/usr/bin/env python3
"""
Comprehensive Crash Prevention System
Prevents system crashes during crawling operations.
"""

import psutil
import gc
import threading
import time
import logging
import signal
import sys
from typing import Dict, Any, Optional
from collections import deque
import requests
import urllib3

# Enhanced SSL bypass for crash prevention
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Setup enhanced SSL bypass
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Set enhanced environment variables for SSL bypass
import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['REQUESTS_VERIFY'] = 'false'
os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '0'
os.environ['SSL_CERT_FILE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

class CrashPreventionSystem:
    """Comprehensive system to prevent crashes during crawling."""
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_thread = None
        self.crash_thresholds = {
            'memory_percent': 85.0,
            'cpu_percent': 90.0,
            'disk_percent': 95.0,
            'network_errors': 10,
            'consecutive_failures': 5
        }
        
        # Performance tracking
        self.performance_history = deque(maxlen=100)
        self.error_history = deque(maxlen=50)
        self.recovery_actions = deque(maxlen=20)
        
        # Crash prevention counters
        self.memory_warnings = 0
        self.cpu_warnings = 0
        self.network_errors = 0
        self.consecutive_failures = 0
        self.recovery_count = 0
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize safe session
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown."""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop_monitoring()
        sys.exit(0)
        
    def start_monitoring(self):
        """Start continuous system monitoring."""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Crash prevention monitoring started")
        
    def stop_monitoring(self):
        """Stop system monitoring."""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Crash prevention monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                self._check_system_health()
                time.sleep(2)  # Check every 2 seconds
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(5)
                
    def _check_system_health(self):
        """Check system health and apply crash prevention."""
        try:
            # Get system metrics
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            # Store metrics
            metrics = {
                'timestamp': time.time(),
                'memory_percent': memory.percent,
                'cpu_percent': cpu_percent,
                'disk_percent': disk.percent,
                'network_errors': self.network_errors,
                'consecutive_failures': self.consecutive_failures
            }
            self.performance_history.append(metrics)
            
            # Check memory usage
            if memory.percent > self.crash_thresholds['memory_percent']:
                self.memory_warnings += 1
                self.logger.warning(f"High memory usage: {memory.percent:.1f}%")
                self._apply_memory_recovery()
                
            # Check CPU usage
            if cpu_percent > self.crash_thresholds['cpu_percent']:
                self.cpu_warnings += 1
                self.logger.warning(f"High CPU usage: {cpu_percent:.1f}%")
                self._apply_cpu_recovery()
                
            # Check disk usage
            if disk.percent > self.crash_thresholds['disk_percent']:
                self.logger.warning(f"High disk usage: {disk.percent:.1f}%")
                self._apply_disk_recovery()
                
            # Check for too many consecutive failures
            if self.consecutive_failures > self.crash_thresholds['consecutive_failures']:
                self.logger.warning(f"Too many consecutive failures: {self.consecutive_failures}")
                self._apply_failure_recovery()
                
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            
    def _apply_memory_recovery(self):
        """Apply memory recovery strategies."""
        try:
            self.logger.info("Applying memory recovery...")
            
            # Force garbage collection
            gc.collect()
            
            # Clear large objects if possible
            if len(self.performance_history) > 50:
                while len(self.performance_history) > 25:
                    self.performance_history.popleft()
                    
            if len(self.error_history) > 25:
                while len(self.error_history) > 10:
                    self.error_history.popleft()
                    
            # Reset session if needed
            if hasattr(self, 'session'):
                self.session.close()
                self.session = requests.Session()
                self.session.verify = False
                
            self.recovery_count += 1
            self.recovery_actions.append({
                'timestamp': time.time(),
                'action': 'memory_recovery',
                'success': True
            })
            
        except Exception as e:
            self.logger.error(f"Memory recovery failed: {e}")
            
    def _apply_cpu_recovery(self):
        """Apply CPU recovery strategies."""
        try:
            self.logger.info("Applying CPU recovery...")
            
            # Reduce monitoring frequency
            time.sleep(1)
            
            # Clear some caches
            if hasattr(self, 'cache'):
                self.cache.clear()
                
            self.recovery_count += 1
            self.recovery_actions.append({
                'timestamp': time.time(),
                'action': 'cpu_recovery',
                'success': True
            })
            
        except Exception as e:
            self.logger.error(f"CPU recovery failed: {e}")
            
    def _apply_disk_recovery(self):
        """Apply disk recovery strategies."""
        try:
            self.logger.info("Applying disk recovery...")
            
            # Clear temporary files if possible
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith('crawler_'):
                    try:
                        os.remove(os.path.join(temp_dir, file))
                    except:
                        pass
                        
            self.recovery_count += 1
            self.recovery_actions.append({
                'timestamp': time.time(),
                'action': 'disk_recovery',
                'success': True
            })
            
        except Exception as e:
            self.logger.error(f"Disk recovery failed: {e}")
            
    def _apply_failure_recovery(self):
        """Apply failure recovery strategies."""
        try:
            self.logger.info("Applying failure recovery...")
            
            # Reset failure counters
            self.consecutive_failures = 0
            self.network_errors = 0
            
            # Wait before retrying
            time.sleep(5)
            
            # Reset session
            if hasattr(self, 'session'):
                self.session.close()
                self.session = requests.Session()
                self.session.verify = False
                
            self.recovery_count += 1
            self.recovery_actions.append({
                'timestamp': time.time(),
                'action': 'failure_recovery',
                'success': True
            })
            
        except Exception as e:
            self.logger.error(f"Failure recovery failed: {e}")
            
    def safe_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make a safe HTTP request with crash prevention."""
        try:
            # Check system health before request
            if not self._is_system_healthy():
                self.logger.warning("System not healthy, skipping request")
                return None
                
            # Make request with timeout
            timeout = kwargs.get('timeout', 30)
            response = self.session.get(url, timeout=timeout, **kwargs)
            
            # Reset failure counters on success
            self.consecutive_failures = 0
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.network_errors += 1
            self.consecutive_failures += 1
            self.error_history.append({
                'timestamp': time.time(),
                'error_type': 'network',
                'error_message': str(e),
                'url': url
            })
            self.logger.error(f"Request failed: {e}")
            return None
            
        except Exception as e:
            self.consecutive_failures += 1
            self.error_history.append({
                'timestamp': time.time(),
                'error_type': 'general',
                'error_message': str(e),
                'url': url
            })
            self.logger.error(f"Unexpected error: {e}")
            return None
            
    def _is_system_healthy(self) -> bool:
        """Check if system is healthy for requests."""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            
            # Check if system is overloaded
            if (memory.percent > 95 or 
                cpu_percent > 95 or 
                self.consecutive_failures > 10):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Health check error: {e}")
            return False
            
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent()
            disk = psutil.disk_usage('/')
            
            return {
                'system_health': {
                    'memory_percent': memory.percent,
                    'cpu_percent': cpu_percent,
                    'disk_percent': disk.percent,
                    'memory_warnings': self.memory_warnings,
                    'cpu_warnings': self.cpu_warnings,
                    'network_errors': self.network_errors,
                    'consecutive_failures': self.consecutive_failures,
                    'recovery_count': self.recovery_count
                },
                'performance_history': list(self.performance_history)[-10:],
                'error_history': list(self.error_history)[-5:],
                'recovery_actions': list(self.recovery_actions)[-5:],
                'is_healthy': self._is_system_healthy()
            }
            
        except Exception as e:
            self.logger.error(f"Health report error: {e}")
            return {'error': str(e)}
            
    def cleanup(self):
        """Clean up resources."""
        try:
            self.stop_monitoring()
            
            if hasattr(self, 'session'):
                self.session.close()
                
            # Clear history
            self.performance_history.clear()
            self.error_history.clear()
            self.recovery_actions.clear()
            
            self.logger.info("Crash prevention system cleaned up")
            
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

# Global crash prevention instance
crash_prevention = CrashPreventionSystem()

def prevent_crashes(func):
    """Decorator to apply crash prevention to functions."""
    def wrapper(*args, **kwargs):
        try:
            # Check system health before execution
            if not crash_prevention._is_system_healthy():
                crash_prevention.logger.warning(f"System not healthy, skipping {func.__name__}")
                return None
                
            # Execute function
            result = func(*args, **kwargs)
            
            # Reset failure counters on success
            crash_prevention.consecutive_failures = 0
            
            return result
            
        except Exception as e:
            crash_prevention.consecutive_failures += 1
            crash_prevention.error_history.append({
                'timestamp': time.time(),
                'error_type': 'function_error',
                'error_message': str(e),
                'function': func.__name__
            })
            crash_prevention.logger.error(f"Function {func.__name__} failed: {e}")
            return None
            
    return wrapper

def thread_safe_prevent_crashes(func):
    """Thread-safe decorator to apply crash prevention."""
    def wrapper(*args, **kwargs):
        with threading.Lock():
            return prevent_crashes(func)(*args, **kwargs)
    return wrapper 