import psutil
import threading
import time
import json
import os
from datetime import datetime
from collections import deque, defaultdict
import numpy as np

class PerformanceMonitor:
    """Advanced performance monitoring system for the crawler"""
    
    def __init__(self, max_history=1000):
        self.max_history = max_history
        self.monitoring_active = False
        self.monitor_thread = None
        
        # System metrics
        self.cpu_history = deque(maxlen=max_history)
        self.memory_history = deque(maxlen=max_history)
        self.disk_history = deque(maxlen=max_history)
        self.network_history = deque(maxlen=max_history)
        
        # Application metrics
        self.crawler_metrics = {
            'datasets_processed': 0,
            'processing_rate': 0,
            'error_rate': 0,
            'ml_classifications': 0,
            'validation_passed': 0,
            'validation_failed': 0,
            'start_time': None,
            'last_update': None
        }
        
        # Performance alerts
        self.alerts = deque(maxlen=50)
        self.alert_thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0,
            'disk_warning': 90.0,
            'processing_rate_min': 1.0  # datasets per minute
        }
        
        # Performance scores
        self.performance_scores = {
            'system_health': 100.0,
            'crawler_efficiency': 100.0,
            'ml_performance': 100.0,
            'overall_score': 100.0
        }
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
    def start_monitoring(self):
        """Start the performance monitoring thread"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            print("✓ Performance monitoring started")
            
    def stop_monitoring(self):
        """Stop the performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("✓ Performance monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                timestamp = datetime.now()
                
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Store metrics
                with self.lock:
                    self.cpu_history.append({
                        'timestamp': timestamp,
                        'cpu_percent': cpu_percent,
                        'cpu_count': psutil.cpu_count(),
                        'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                    })
                    
                    self.memory_history.append({
                        'timestamp': timestamp,
                        'memory_percent': memory.percent,
                        'memory_used_gb': memory.used / (1024**3),
                        'memory_available_gb': memory.available / (1024**3),
                        'memory_total_gb': memory.total / (1024**3)
                    })
                    
                    self.disk_history.append({
                        'timestamp': timestamp,
                        'disk_percent': (disk.used / disk.total) * 100,
                        'disk_used_gb': disk.used / (1024**3),
                        'disk_free_gb': disk.free / (1024**3),
                        'disk_total_gb': disk.total / (1024**3)
                    })
                    
                    self.network_history.append({
                        'timestamp': timestamp,
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                        'packets_recv': network.packets_recv
                    })
                
                # Check for alerts
                self._check_alerts(cpu_percent, memory.percent, (disk.used / disk.total) * 100)
                
                # Update performance scores
                self._update_performance_scores()
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(10)
                
    def _check_alerts(self, cpu_percent, memory_percent, disk_percent):
        """Check for performance alerts"""
        alerts = []
        
        # CPU alerts
        if cpu_percent >= self.alert_thresholds['cpu_critical']:
            alerts.append(f"CRITICAL: CPU usage at {cpu_percent:.1f}%")
        elif cpu_percent >= self.alert_thresholds['cpu_warning']:
            alerts.append(f"WARNING: CPU usage at {cpu_percent:.1f}%")
            
        # Memory alerts
        if memory_percent >= self.alert_thresholds['memory_critical']:
            alerts.append(f"CRITICAL: Memory usage at {memory_percent:.1f}%")
        elif memory_percent >= self.alert_thresholds['memory_warning']:
            alerts.append(f"WARNING: Memory usage at {memory_percent:.1f}%")
            
        # Disk alerts
        if disk_percent >= self.alert_thresholds['disk_warning']:
            alerts.append(f"WARNING: Disk usage at {disk_percent:.1f}%")
            
        # Add alerts to history
        for alert in alerts:
            self.alerts.append({
                'timestamp': datetime.now(),
                'message': alert,
                'level': 'CRITICAL' if 'CRITICAL' in alert else 'WARNING'
            })
            
    def _update_performance_scores(self):
        """Update performance scores based on current metrics"""
        with self.lock:
            # System health score
            cpu_avg = np.mean([m['cpu_percent'] for m in list(self.cpu_history)[-10:]]) if self.cpu_history else 0
            memory_avg = np.mean([m['memory_percent'] for m in list(self.memory_history)[-10:]]) if self.memory_history else 0
            
            system_health = 100 - (cpu_avg * 0.4 + memory_avg * 0.6)
            self.performance_scores['system_health'] = max(0, system_health)
            
            # Crawler efficiency score
            if self.crawler_metrics['start_time']:
                runtime = (datetime.now() - self.crawler_metrics['start_time']).total_seconds() / 60
                if runtime > 0:
                    processing_rate = self.crawler_metrics['datasets_processed'] / runtime
                    efficiency = min(100, (processing_rate / 10) * 100)  # Target: 10 datasets/minute
                    self.performance_scores['crawler_efficiency'] = efficiency
                    
            # ML performance score
            if self.crawler_metrics['datasets_processed'] > 0:
                ml_usage_rate = self.crawler_metrics['ml_classifications'] / self.crawler_metrics['datasets_processed']
                self.performance_scores['ml_performance'] = ml_usage_rate * 100
                
            # Overall score
            self.performance_scores['overall_score'] = np.mean([
                self.performance_scores['system_health'],
                self.performance_scores['crawler_efficiency'],
                self.performance_scores['ml_performance']
            ])
            
    def update_crawler_metrics(self, **kwargs):
        """Update crawler-specific metrics"""
        with self.lock:
            for key, value in kwargs.items():
                if key in self.crawler_metrics:
                    self.crawler_metrics[key] = value
            self.crawler_metrics['last_update'] = datetime.now()
            
    def get_current_metrics(self):
        """Get current performance metrics"""
        with self.lock:
            return {
                'system': {
                    'cpu': self.cpu_history[-1] if self.cpu_history else None,
                    'memory': self.memory_history[-1] if self.memory_history else None,
                    'disk': self.disk_history[-1] if self.disk_history else None,
                    'network': self.network_history[-1] if self.network_history else None
                },
                'crawler': self.crawler_metrics.copy(),
                'performance_scores': self.performance_scores.copy(),
                'alerts': list(self.alerts)[-10:]  # Last 10 alerts
            }
            
    def get_performance_summary(self):
        """Get a performance summary for the dashboard"""
        metrics = self.get_current_metrics()
        
        summary = {
            'system_health': {
                'score': metrics['performance_scores']['system_health'],
                'status': 'Good' if metrics['performance_scores']['system_health'] > 70 else 'Warning' if metrics['performance_scores']['system_health'] > 40 else 'Critical'
            },
            'crawler_efficiency': {
                'score': metrics['performance_scores']['crawler_efficiency'],
                'status': 'Good' if metrics['performance_scores']['crawler_efficiency'] > 70 else 'Warning' if metrics['performance_scores']['crawler_efficiency'] > 40 else 'Poor'
            },
            'ml_performance': {
                'score': metrics['performance_scores']['ml_performance'],
                'status': 'Good' if metrics['performance_scores']['ml_performance'] > 70 else 'Warning' if metrics['performance_scores']['ml_performance'] > 40 else 'Poor'
            },
            'overall_score': metrics['performance_scores']['overall_score'],
            'active_alerts': len([a for a in metrics['alerts'] if a['level'] == 'CRITICAL']),
            'warnings': len([a for a in metrics['alerts'] if a['level'] == 'WARNING'])
        }
        
        return summary
        
    def export_metrics(self, filename=None):
        """Export performance metrics to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"performance_metrics_{timestamp}.json"
            
        metrics = {
            'export_timestamp': datetime.now().isoformat(),
            'system_metrics': {
                'cpu_history': list(self.cpu_history),
                'memory_history': list(self.memory_history),
                'disk_history': list(self.disk_history),
                'network_history': list(self.network_history)
            },
            'crawler_metrics': self.crawler_metrics,
            'performance_scores': self.performance_scores,
            'alerts': list(self.alerts)
        }
        
        with open(filename, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
            
        return filename

# Global performance monitor instance
performance_monitor = PerformanceMonitor() 