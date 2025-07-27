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
        """Enhanced monitoring loop with advanced metrics collection"""
        while self.monitoring_active:
            try:
                timestamp = datetime.now()
                
                # Enhanced system metrics collection
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network = psutil.net_io_counters()
                
                # Enhanced CPU metrics
                cpu_info = {
                        'timestamp': timestamp,
                        'cpu_percent': cpu_percent,
                        'cpu_count': psutil.cpu_count(),
                    'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                    'cpu_load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                    'cpu_temperature': self._get_cpu_temperature()
                }
                
                # Enhanced memory metrics
                memory_info = {
                        'timestamp': timestamp,
                        'memory_percent': memory.percent,
                        'memory_used_gb': memory.used / (1024**3),
                        'memory_available_gb': memory.available / (1024**3),
                    'memory_total_gb': memory.total / (1024**3),
                    'memory_swap_percent': psutil.swap_memory().percent if hasattr(psutil, 'swap_memory') else None,
                    'memory_swap_used_gb': psutil.swap_memory().used / (1024**3) if hasattr(psutil, 'swap_memory') else None
                }
                
                # Enhanced disk metrics
                disk_info = {
                        'timestamp': timestamp,
                    'disk_percent': disk.percent,
                        'disk_used_gb': disk.used / (1024**3),
                        'disk_free_gb': disk.free / (1024**3),
                    'disk_total_gb': disk.total / (1024**3),
                    'disk_io': self._get_disk_io_stats()
                }
                    
                # Enhanced network metrics
                network_info = {
                        'timestamp': timestamp,
                        'bytes_sent': network.bytes_sent,
                        'bytes_recv': network.bytes_recv,
                        'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv,
                    'network_connections': len(psutil.net_connections()) if hasattr(psutil, 'net_connections') else 0
                }
                
                # Store enhanced metrics
                with self.lock:
                    self.cpu_history.append(cpu_info)
                    self.memory_history.append(memory_info)
                    self.disk_history.append(disk_info)
                    self.network_history.append(network_info)
                
                # Enhanced alert checking
                self._check_enhanced_alerts(cpu_percent, memory.percent, disk.percent)
                
                # Update performance scores
                self._update_enhanced_performance_scores()
                
                # Enhanced logging
                if self.monitoring_active:
                    self._log_performance_metrics(timestamp, cpu_percent, memory.percent, disk.percent)
                
                time.sleep(2)  # Monitor every 2 seconds for more responsive alerts
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                time.sleep(5)  # Wait longer on error
    
    def _get_cpu_temperature(self):
        """Get CPU temperature if available"""
        try:
            # Try to get CPU temperature (platform dependent)
            if hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            if entry.current > 0:
                                return entry.current
        except:
            pass
        return None
    
    def _get_disk_io_stats(self):
        """Get disk I/O statistics"""
        try:
            if hasattr(psutil, 'disk_io_counters'):
                io_stats = psutil.disk_io_counters()
                return {
                    'read_bytes': io_stats.read_bytes,
                    'write_bytes': io_stats.write_bytes,
                    'read_count': io_stats.read_count,
                    'write_count': io_stats.write_count
                }
        except:
            pass
        return None
    
    def _check_enhanced_alerts(self, cpu_percent, memory_percent, disk_percent):
        """Enhanced alert checking with multiple thresholds and severity levels"""
        alerts = []
        
        # CPU alerts with multiple severity levels
        if cpu_percent > self.alert_thresholds['cpu_critical']:
            alerts.append({
                'type': 'cpu_critical',
                'message': f'Critical CPU usage: {cpu_percent:.1f}%',
                'severity': 'critical',
                'timestamp': datetime.now(),
                'value': cpu_percent
            })
        elif cpu_percent > self.alert_thresholds['cpu_warning']:
            alerts.append({
                'type': 'cpu_warning',
                'message': f'High CPU usage: {cpu_percent:.1f}%',
                'severity': 'warning',
                'timestamp': datetime.now(),
                'value': cpu_percent
            })
            
        # Memory alerts
        if memory_percent > self.alert_thresholds['memory_critical']:
            alerts.append({
                'type': 'memory_critical',
                'message': f'Critical memory usage: {memory_percent:.1f}%',
                'severity': 'critical',
                'timestamp': datetime.now(),
                'value': memory_percent
            })
        elif memory_percent > self.alert_thresholds['memory_warning']:
            alerts.append({
                'type': 'memory_warning',
                'message': f'High memory usage: {memory_percent:.1f}%',
                'severity': 'warning',
                'timestamp': datetime.now(),
                'value': memory_percent
            })
            
        # Disk alerts
        if disk_percent > self.alert_thresholds['disk_warning']:
            alerts.append({
                'type': 'disk_warning',
                'message': f'High disk usage: {disk_percent:.1f}%',
                'severity': 'warning',
                'timestamp': datetime.now(),
                'value': disk_percent
            })
        
        # Processing rate alerts
        if hasattr(self, 'crawler_metrics') and self.crawler_metrics.get('processing_rate', 0) < self.alert_thresholds['processing_rate_min']:
            alerts.append({
                'type': 'processing_rate_low',
                'message': f'Low processing rate: {self.crawler_metrics["processing_rate"]:.2f} datasets/min',
                'severity': 'warning',
                'timestamp': datetime.now(),
                'value': self.crawler_metrics['processing_rate']
            })
        
        # Add alerts to queue
        for alert in alerts:
            self.alerts.append(alert)
            print(f"🚨 {alert['severity'].upper()}: {alert['message']}")
    
    def _update_enhanced_performance_scores(self):
        """Update enhanced performance scores with more sophisticated calculations"""
        try:
            # Calculate system health score
            cpu_score = 100 - (self.cpu_history[-1]['cpu_percent'] if self.cpu_history else 0)
            memory_score = 100 - (self.memory_history[-1]['memory_percent'] if self.memory_history else 0)
            disk_score = 100 - (self.disk_history[-1]['disk_percent'] if self.disk_history else 0)
            
            # Weighted system health calculation
            self.performance_scores['system_health'] = (
                cpu_score * 0.4 + 
                memory_score * 0.4 + 
                disk_score * 0.2
            )
            
            # Enhanced crawler efficiency score
            if hasattr(self, 'crawler_metrics'):
                processing_rate = self.crawler_metrics.get('processing_rate', 0)
                error_rate = self.crawler_metrics.get('error_rate', 0)
                
                # Normalize processing rate (assume 10 datasets/min is optimal)
                rate_score = min(processing_rate / 10.0 * 100, 100)
                error_score = max(100 - error_rate * 100, 0)
                
                self.performance_scores['crawler_efficiency'] = (
                    rate_score * 0.7 + 
                    error_score * 0.3
                )
                    
            # ML performance score
            if hasattr(self, 'crawler_metrics'):
                ml_classifications = self.crawler_metrics.get('ml_classifications', 0)
                total_processed = self.crawler_metrics.get('datasets_processed', 0)
                
                if total_processed > 0:
                    ml_usage_rate = ml_classifications / total_processed
                    self.performance_scores['ml_performance'] = ml_usage_rate * 100
                else:
                    self.performance_scores['ml_performance'] = 0
            
            # Overall score with enhanced weighting
            self.performance_scores['overall_score'] = (
                self.performance_scores['system_health'] * 0.3 +
                self.performance_scores['crawler_efficiency'] * 0.4 +
                self.performance_scores['ml_performance'] * 0.3
            )
            
        except Exception as e:
            print(f"Error updating performance scores: {e}")
    
    def _log_performance_metrics(self, timestamp, cpu_percent, memory_percent, disk_percent):
        """Enhanced performance metrics logging"""
        try:
            log_entry = {
                'timestamp': timestamp.isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'system_health': self.performance_scores['system_health'],
                'crawler_efficiency': self.performance_scores['crawler_efficiency'],
                'ml_performance': self.performance_scores['ml_performance'],
                'overall_score': self.performance_scores['overall_score']
            }
            
            # Log to file if enabled
            if self.config.get('log_performance', True):
                log_file = f"performance_{timestamp.strftime('%Y%m%d')}.log"
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')
                    
        except Exception as e:
            print(f"Error logging performance metrics: {e}")
    
    def get_enhanced_metrics(self):
        """Get enhanced performance metrics with detailed analysis"""
        try:
            current_metrics = self.get_current_metrics()
            
            # Add enhanced analysis
            enhanced_metrics = {
                **current_metrics,
                'trends': self._calculate_trends(),
                'predictions': self._predict_performance(),
                'recommendations': self._generate_recommendations(),
                'alerts_summary': self._get_alerts_summary()
            }
            
            return enhanced_metrics
            
        except Exception as e:
            print(f"Error getting enhanced metrics: {e}")
            return self.get_current_metrics()
    
    def _calculate_trends(self):
        """Calculate performance trends over time"""
        trends = {}
        
        try:
            # CPU trend
            if len(self.cpu_history) > 10:
                recent_cpu = [entry['cpu_percent'] for entry in self.cpu_history[-10:]]
                trends['cpu_trend'] = {
                    'direction': 'increasing' if recent_cpu[-1] > recent_cpu[0] else 'decreasing',
                    'change_rate': (recent_cpu[-1] - recent_cpu[0]) / len(recent_cpu),
                    'stability': 'stable' if max(recent_cpu) - min(recent_cpu) < 10 else 'volatile'
                }
            
            # Memory trend
            if len(self.memory_history) > 10:
                recent_memory = [entry['memory_percent'] for entry in self.memory_history[-10:]]
                trends['memory_trend'] = {
                    'direction': 'increasing' if recent_memory[-1] > recent_memory[0] else 'decreasing',
                    'change_rate': (recent_memory[-1] - recent_memory[0]) / len(recent_memory),
                    'stability': 'stable' if max(recent_memory) - min(recent_memory) < 5 else 'volatile'
                }
            
        except Exception as e:
            print(f"Error calculating trends: {e}")
        
        return trends
    
    def _predict_performance(self):
        """Predict future performance based on current trends"""
        predictions = {}
        
        try:
            # Simple linear prediction for next 5 minutes
            if len(self.cpu_history) > 5:
                cpu_values = [entry['cpu_percent'] for entry in self.cpu_history[-5:]]
                cpu_slope = (cpu_values[-1] - cpu_values[0]) / len(cpu_values)
                predictions['cpu_prediction'] = {
                    'next_5min': min(100, max(0, cpu_values[-1] + cpu_slope * 5)),
                    'trend': 'increasing' if cpu_slope > 0 else 'decreasing'
                }
            
        except Exception as e:
            print(f"Error predicting performance: {e}")
        
        return predictions
    
    def _generate_recommendations(self):
        """Generate performance recommendations"""
        recommendations = []
        
        try:
            current_metrics = self.get_current_metrics()
            
            # CPU recommendations
            if current_metrics['cpu_percent'] > 80:
                recommendations.append({
                    'type': 'cpu_optimization',
                    'priority': 'high',
                    'message': 'Consider reducing concurrent processing or optimizing algorithms',
                    'action': 'Reduce max_concurrent_requests in configuration'
                })
            
            # Memory recommendations
            if current_metrics['memory_percent'] > 85:
                recommendations.append({
                    'type': 'memory_optimization',
                    'priority': 'high',
                    'message': 'High memory usage detected. Consider clearing caches or reducing batch sizes',
                    'action': 'Clear ML model cache or reduce batch processing size'
                })
            
            # Processing rate recommendations
            if hasattr(self, 'crawler_metrics') and self.crawler_metrics.get('processing_rate', 0) < 2:
                recommendations.append({
                    'type': 'performance_optimization',
                    'priority': 'medium',
                    'message': 'Low processing rate. Check for bottlenecks in data extraction or ML processing',
                    'action': 'Review extraction algorithms and ML model loading'
                })
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
        
        return recommendations
    
    def _get_alerts_summary(self):
        """Get summary of recent alerts"""
        try:
            recent_alerts = list(self.alerts)[-10:]  # Last 10 alerts
            
            alert_summary = {
                'total_alerts': len(recent_alerts),
                'critical_alerts': len([a for a in recent_alerts if a['severity'] == 'critical']),
                'warning_alerts': len([a for a in recent_alerts if a['severity'] == 'warning']),
                'recent_alerts': recent_alerts[-5:]  # Last 5 alerts
            }
            
            return alert_summary
            
        except Exception as e:
            print(f"Error getting alerts summary: {e}")
            return {}
            
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