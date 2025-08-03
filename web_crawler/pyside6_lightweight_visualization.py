#!/usr/bin/env python3
"""
PySide6 Lightweight Live ML Visualization
- 1 second updates to reduce memory usage
- Simple line charts with connected points
- Real crawler data integration
- Minimal memory footprint
"""

import sys
import time
import threading
import numpy as np
import psutil
import gc
from collections import deque
from typing import Dict, List, Any, Optional
import json
import logging

# PySide6 imports
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QFrame, QGridLayout,
                               QTextEdit, QScrollArea, QSplitter, QTabWidget)
from PySide6.QtCore import QTimer, Qt, QThread, Signal, QPointF
from PySide6.QtGui import QFont, QPalette, QColor, QPainter, QPen, QBrush
from PySide6.QtCharts import (QChart, QChartView, QLineSeries, QValueAxis, 
                             QDateTimeAxis, QSplineSeries, QScatterSeries)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LightweightDataCollectorThread(QThread):
    """Lightweight thread for collecting ML metrics data - 1 second updates"""
    data_ready = Signal(dict)
    
    def __init__(self, crawler_instance=None, active_metrics=None):
        super().__init__()
        self.crawler = crawler_instance
        self.running = True
        self.start_time = time.time()
        self.active_metrics = active_metrics or set()
        self.last_data = {}
        self.crawl_active = False
        
    def set_active_metrics(self, metrics):
        """Set which metrics to track"""
        self.active_metrics = set(metrics)
        logger.info(f"Active metrics: {self.active_metrics}")
    
    def set_crawl_active(self, active):
        """Set whether real crawling is active"""
        self.crawl_active = active
        logger.info(f"Crawl active: {active}")
    
    def run(self):
        """Run lightweight data collection - 1 second intervals"""
        while self.running:
            try:
                current_time = time.time() - self.start_time
                
                # Only collect data for active metrics
                if self.active_metrics:
                    if self.crawl_active and self.crawler:
                        data = self.collect_real_crawler_data(current_time)
                    else:
                        data = self.generate_simulated_data_lightweight(current_time)
                    
                    # Emit data signal
                    self.data_ready.emit(data)
                
                # Sleep for 1 second to reduce memory usage
                time.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Data collection error: {e}")
                time.sleep(1)
    
    def collect_real_crawler_data(self, current_time):
        """Collect real data from active crawler"""
        data = {'timestamp': current_time}
        
        try:
            # Get real metrics from crawler
            if hasattr(self.crawler, 'extracted_data') and self.crawler.extracted_data:
                # Calculate real metrics from extracted data
                total_items = len(self.crawler.extracted_data)
                if total_items > 0:
                    # Calculate accuracy from extracted data
                    accuracies = []
                    confidences = []
                    processing_times = []
                    
                    for item in self.crawler.extracted_data:
                        if 'confidence' in item:
                            confidences.append(item['confidence'])
                        if 'quality' in item:
                            accuracies.append(item['quality'])
                        if 'processing_time' in item:
                            processing_times.append(item['processing_time'])
                    
                    # Calculate metrics
                    if 'classification_accuracy' in self.active_metrics and accuracies:
                        data['classification_accuracy'] = np.mean(accuracies)
                    
                    if 'confidence_scores' in self.active_metrics and confidences:
                        data['confidence_scores'] = np.mean(confidences)
                    
                    if 'processing_time' in self.active_metrics and processing_times:
                        data['processing_time'] = np.mean(processing_times)
                    
                    # Calculate RMS error from confidence scores
                    if 'rms_error' in self.active_metrics and confidences:
                        errors = [1.0 - c for c in confidences]
                        data['rms_error'] = np.sqrt(np.mean(np.square(errors)))
                    
                    # Calculate standard error
                    if 'standard_error' in self.active_metrics and confidences:
                        std_dev = np.std(confidences)
                        n = len(confidences)
                        data['standard_error'] = std_dev / np.sqrt(n) if n > 0 else 0.1
                    
                    # Memory usage
                    if 'memory_usage' in self.active_metrics:
                        data['memory_usage'] = psutil.virtual_memory().percent
                    
                    # BERT vs Fallback accuracy
                    if 'bert_accuracy' in self.active_metrics or 'fallback_accuracy' in self.active_metrics:
                        # Estimate based on crawler state
                        bert_available = hasattr(self.crawler, 'bert_optimizer') and self.crawler.bert_optimizer
                        data['bert_accuracy'] = 0.85 if bert_available else 0.65
                        data['fallback_accuracy'] = 0.70 if bert_available else 0.60
                    
                    # Weight performance
                    if 'weight_performance' in self.active_metrics:
                        if hasattr(self.crawler, 'bert_optimizer') and self.crawler.bert_optimizer:
                            data['weight_performance'] = 0.78
                        else:
                            data['weight_performance'] = 0.65
                    
                    # Quality scores
                    if 'quality_scores' in self.active_metrics and accuracies:
                        data['quality_scores'] = np.mean(accuracies)
                    
            else:
                # No data yet, use fallback
                data = self.generate_simulated_data_lightweight(current_time)
            
        except Exception as e:
            logger.error(f"Real crawler data collection error: {e}")
            data = self.generate_simulated_data_lightweight(current_time)
        
        return data
    
    def generate_simulated_data_lightweight(self, current_time):
        """Generate lightweight simulated data"""
        data = {'timestamp': current_time}
        
        # Only generate active metrics
        if 'rms_error' in self.active_metrics or 'standard_error' in self.active_metrics:
            data['rms_error'] = self.generate_rms_error_lightweight()
            data['standard_error'] = self.generate_standard_error_lightweight()
        
        if 'classification_accuracy' in self.active_metrics:
            data['classification_accuracy'] = self.generate_accuracy_lightweight()
        
        if 'confidence_scores' in self.active_metrics:
            data['confidence_scores'] = self.generate_confidence_lightweight()
        
        if 'processing_time' in self.active_metrics:
            data['processing_time'] = self.generate_processing_time_lightweight()
        
        if 'memory_usage' in self.active_metrics:
            data['memory_usage'] = psutil.virtual_memory().percent
        
        if 'bert_accuracy' in self.active_metrics or 'fallback_accuracy' in self.active_metrics:
            data['bert_accuracy'] = self.generate_bert_accuracy_lightweight()
            data['fallback_accuracy'] = self.generate_fallback_accuracy_lightweight()
        
        if 'weight_performance' in self.active_metrics:
            data['weight_performance'] = self.generate_weight_performance_lightweight()
        
        if 'quality_scores' in self.active_metrics:
            data['quality_scores'] = self.generate_quality_scores_lightweight()
        
        return data
    
    # Lightweight data generation methods
    def generate_rms_error_lightweight(self):
        base_error = 0.25
        time_factor = (time.time() - self.start_time) / 100
        learning_factor = np.exp(-time_factor)
        noise = np.random.normal(0, 0.02)
        return max(0.01, base_error * learning_factor + noise)
    
    def generate_standard_error_lightweight(self):
        base_error = 0.12
        time_factor = (time.time() - self.start_time) / 50
        sample_size_factor = 1 / (1 + time_factor)
        noise = np.random.normal(0, 0.01)
        return max(0.005, base_error * sample_size_factor + noise)
    
    def generate_accuracy_lightweight(self):
        base_accuracy = 0.75
        time_factor = (time.time() - self.start_time) / 200
        improvement_factor = 1 - np.exp(-time_factor)
        noise = np.random.normal(0, 0.03)
        return min(0.95, base_accuracy + improvement_factor * 0.2 + noise)
    
    def generate_confidence_lightweight(self):
        accuracy = self.generate_accuracy_lightweight()
        noise = np.random.normal(0, 0.05)
        return min(1.0, max(0.1, accuracy + noise))
    
    def generate_processing_time_lightweight(self):
        base_time = 1.5
        complexity_factor = np.random.exponential(0.5)
        return base_time + complexity_factor
    
    def generate_bert_accuracy_lightweight(self):
        base_accuracy = 0.88
        time_factor = (time.time() - self.start_time) / 150
        improvement_factor = 1 - np.exp(-time_factor)
        noise = np.random.normal(0, 0.02)
        return min(0.95, base_accuracy + improvement_factor * 0.07 + noise)
    
    def generate_fallback_accuracy_lightweight(self):
        base_accuracy = 0.68
        noise = np.random.normal(0, 0.03)
        return min(0.8, max(0.5, base_accuracy + noise))
    
    def generate_weight_performance_lightweight(self):
        base_performance = 0.78
        time_factor = (time.time() - self.start_time) / 100
        optimization_factor = 1 - np.exp(-time_factor)
        noise = np.random.normal(0, 0.04)
        return min(0.95, base_performance + optimization_factor * 0.15 + noise)
    
    def generate_quality_scores_lightweight(self):
        base_quality = 0.65
        time_factor = (time.time() - self.start_time) / 80
        improvement_factor = 1 - np.exp(-time_factor)
        noise = np.random.normal(0, 0.03)
        return min(0.95, base_quality + improvement_factor * 0.25 + noise)
    
    def stop(self):
        """Stop the data collection thread"""
        self.running = False

class LightweightChartWidget(QWidget):
    """Widget for displaying lightweight charts with simple line connections"""
    
    def __init__(self, title, max_points=60):
        super().__init__()
        self.title = title
        self.max_points = max_points
        self.rms_series = QLineSeries()  # Use simple line series
        self.standard_error_series = QLineSeries()
        self.setup_chart()
    
    def setup_chart(self):
        """Setup the lightweight chart"""
        # Create chart
        self.chart = QChart()
        self.chart.setTitle(self.title)
        self.chart.setAnimationOptions(QChart.NoAnimation)  # Disable animations for performance
        
        # Create axes
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Time (s)")
        self.axis_x.setRange(1, 60)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Value")
        self.axis_y.setRange(0, 1)
        
        # Add series to chart
        self.chart.addSeries(self.rms_series)
        self.chart.addSeries(self.standard_error_series)
        
        # Attach axes
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.rms_series.attachAxis(self.axis_x)
        self.rms_series.attachAxis(self.axis_y)
        self.standard_error_series.attachAxis(self.axis_x)
        self.standard_error_series.attachAxis(self.axis_y)
        
        # Set series names
        self.rms_series.setName("RMS Error")
        self.standard_error_series.setName("Standard Error")
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def update_data(self, timestamp, rms_value, standard_error_value):
        """Update chart with new data point using sliding window"""
        # Add new points
        self.rms_series.append(timestamp, rms_value)
        self.standard_error_series.append(timestamp, standard_error_value)
        
        # Implement sliding window: remove old points when we exceed 60 seconds
        if self.rms_series.count() > 0:
            first_point = self.rms_series.points()[0]
            if first_point.x() < timestamp - 60:
                # Remove points older than 60 seconds
                while self.rms_series.count() > 0 and self.rms_series.points()[0].x() < timestamp - 60:
                    self.rms_series.remove(self.rms_series.points()[0])
                while self.standard_error_series.count() > 0 and self.standard_error_series.points()[0].x() < timestamp - 60:
                    self.standard_error_series.remove(self.standard_error_series.points()[0])
        
        # Update axis range to show sliding window
        if self.rms_series.count() > 1:
            points = self.rms_series.points()
            if points:
                min_x = max(1, timestamp - 60)
                max_x = timestamp
                self.axis_x.setRange(min_x, max_x)
                
                # Update Y axis based on current values
                y_values = [p.y() for p in points]
                y_values.extend([p.y() for p in self.standard_error_series.points()])
                if y_values:
                    min_y = max(0, min(y_values) - 0.05)
                    max_y = min(1, max(y_values) + 0.05)
                    self.axis_y.setRange(min_y, max_y)
    
    def reset_chart(self):
        """Reset the chart data"""
        self.rms_series.clear()
        self.standard_error_series.clear()
        self.axis_x.setRange(1, 60)
        self.axis_y.setRange(0, 1)

class SingleMetricLightweightChartWidget(QWidget):
    """Widget for displaying a single metric with lightweight chart"""
    
    def __init__(self, title, max_points=60):
        super().__init__()
        self.title = title
        self.max_points = max_points
        self.series = QLineSeries()  # Use simple line series
        self.setup_chart()
    
    def setup_chart(self):
        """Setup the lightweight chart"""
        # Create chart
        self.chart = QChart()
        self.chart.addSeries(self.series)
        self.chart.setTitle(self.title)
        self.chart.setAnimationOptions(QChart.NoAnimation)  # Disable animations
        
        # Create axes
        self.axis_x = QValueAxis()
        self.axis_x.setTitleText("Time (s)")
        self.axis_x.setRange(1, 60)
        
        self.axis_y = QValueAxis()
        self.axis_y.setTitleText("Value")
        self.axis_y.setRange(0, 1)
        
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_x)
        self.series.attachAxis(self.axis_y)
        
        # Create chart view
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.chart_view)
        self.setLayout(layout)
    
    def update_data(self, timestamp, value):
        """Update chart with new data point using sliding window"""
        # Add new point
        self.series.append(timestamp, value)
        
        # Implement sliding window: remove old points when we exceed 60 seconds
        if self.series.count() > 0:
            first_point = self.series.points()[0]
            if first_point.x() < timestamp - 60:
                # Remove points older than 60 seconds
                while self.series.count() > 0 and self.series.points()[0].x() < timestamp - 60:
                    self.series.remove(self.series.points()[0])
        
        # Update axis range to show sliding window
        if self.series.count() > 1:
            points = self.series.points()
            if points:
                min_x = max(1, timestamp - 60)
                max_x = timestamp
                self.axis_x.setRange(min_x, max_x)
                
                # Update Y axis based on current values
                y_values = [p.y() for p in points]
                if y_values:
                    min_y = max(0, min(y_values) - 0.05)
                    max_y = min(1, max(y_values) + 0.05)
                    self.axis_y.setRange(min_y, max_y)
    
    def reset_chart(self):
        """Reset the chart data"""
        self.series.clear()
        self.axis_x.setRange(1, 60)
        self.axis_y.setRange(0, 1)

class ConsoleMetricsWidget(QWidget):
    """Widget for displaying metrics in console-style format"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.metrics_data = {}
    
    def setup_ui(self):
        """Setup the console-style UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Live ML Metrics Console")
        title.setFont(QFont("Consolas", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Console text area
        self.console_text = QTextEdit()
        self.console_text.setFont(QFont("Consolas", 10))
        self.console_text.setMaximumHeight(200)
        self.console_text.setReadOnly(True)
        layout.addWidget(self.console_text)
        
        self.setLayout(layout)
    
    def update_metrics(self, data):
        """Update console with new metrics"""
        self.metrics_data = data
        
        # Format console output
        console_output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           LIVE ML METRICS CONSOLE                           ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  RMS Error:        {data.get('rms_error', 0):.4f}                           ║
║  Standard Error:   {data.get('standard_error', 0):.4f}                      ║
║  Accuracy:         {data.get('classification_accuracy', 0):.4f}              ║
║  Confidence:       {data.get('confidence_scores', 0):.4f}                   ║
║  Processing Time:  {data.get('processing_time', 0):.3f}s                    ║
║  Memory Usage:     {data.get('memory_usage', 0):.1f}%                      ║
║  BERT Accuracy:    {data.get('bert_accuracy', 0):.4f}                       ║
║  Fallback Acc:     {data.get('fallback_accuracy', 0):.4f}                   ║
║  Weight Perf:      {data.get('weight_performance', 0):.4f}                  ║
║  Quality Score:    {data.get('quality_scores', 0):.4f}                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Timestamp:        {data.get('timestamp', 0):.2f}s                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        
        self.console_text.setText(console_output)

class PySide6LightweightVisualization(QMainWindow):
    """Main window for lightweight PySide6 live ML visualization"""
    
    def __init__(self, crawler_instance=None):
        super().__init__()
        self.crawler = crawler_instance
        self.current_chart = None
        self.active_metrics = set()
        self.setup_ui()
        self.setup_data_collection()
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("PySide6 Lightweight ML Visualization")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Create tab widget for charts
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tab_widget)
        
        # Create charts
        self.setup_charts()
        
        # Create status panel
        status_panel = self.create_status_panel()
        main_layout.addWidget(status_panel)
        
        # Style the window
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
        """)
    
    def create_control_panel(self):
        """Create control panel"""
        panel = QFrame()
        layout = QHBoxLayout(panel)
        
        # Control buttons
        self.start_button = QPushButton("Start Real Crawling")
        self.start_button.clicked.connect(self.start_real_crawling)
        layout.addWidget(self.start_button)
        
        self.simulation_button = QPushButton("Start Simulation")
        self.simulation_button.clicked.connect(self.start_simulation)
        layout.addWidget(self.simulation_button)
        
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_visualization)
        layout.addWidget(self.stop_button)
        
        self.reset_button = QPushButton("Reset Current Chart")
        self.reset_button.clicked.connect(self.reset_current_chart)
        layout.addWidget(self.reset_button)
        
        self.export_button = QPushButton("Export Data")
        self.export_button.clicked.connect(self.export_data)
        layout.addWidget(self.export_button)
        
        # Performance info
        self.performance_label = QLabel("CPU: 0% | Memory: 0%")
        self.performance_label.setStyleSheet("color: #666; font-weight: normal;")
        layout.addWidget(self.performance_label)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #666; font-weight: normal;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        return panel
    
    def setup_charts(self):
        """Setup all charts in tabs with lightweight implementation"""
        self.charts = {}
        
        # Create combined RMS + Standard Error chart
        self.charts['error_metrics'] = LightweightChartWidget("RMS Error + Standard Error")
        self.tab_widget.addTab(self.charts['error_metrics'], "Error Metrics")
        
        # Create single metric charts
        single_metrics = [
            ('Classification Accuracy', 'classification_accuracy'),
            ('Confidence Scores', 'confidence_scores'),
            ('Processing Time', 'processing_time'),
            ('Memory Usage', 'memory_usage'),
            ('BERT vs Fallback', 'bert_accuracy'),
            ('Weight Performance', 'weight_performance'),
            ('Quality Scores', 'quality_scores')
        ]
        
        for title, key in single_metrics:
            chart_widget = SingleMetricLightweightChartWidget(title)
            self.charts[key] = chart_widget
            self.tab_widget.addTab(chart_widget, title)
        
        # Add console tab
        self.console_widget = ConsoleMetricsWidget()
        self.tab_widget.addTab(self.console_widget, "Console")
    
    def on_tab_changed(self, index):
        """Handle tab change - update active metrics"""
        if index < len(self.charts):
            # Get the chart widget for the current tab
            chart_key = list(self.charts.keys())[index]
            chart_widget = self.charts[chart_key]
            chart_widget.reset_chart()
            self.current_chart = chart_key
            
            # Update active metrics based on current tab
            self.update_active_metrics(chart_key)
            
            self.status_label.setText(f"Status: Switched to {chart_key} chart")
    
    def update_active_metrics(self, chart_key):
        """Update which metrics are actively tracked"""
        if chart_key == 'error_metrics':
            self.active_metrics = {'rms_error', 'standard_error'}
        elif chart_key in self.charts:
            self.active_metrics = {chart_key}
        else:
            self.active_metrics = set()
        
        # Update data collector
        if hasattr(self, 'data_thread'):
            self.data_thread.set_active_metrics(self.active_metrics)
    
    def create_status_panel(self):
        """Create status panel with metrics"""
        panel = QFrame()
        layout = QGridLayout(panel)
        
        # Create metric labels
        self.metric_labels = {}
        metrics = [
            ('RMS Error', '0.000'),
            ('Standard Error', '0.000'),
            ('Accuracy', '0.000'),
            ('Confidence', '0.000'),
            ('Processing Time', '0.000s'),
            ('Memory Usage', '0.0%'),
            ('BERT Accuracy', '0.000'),
            ('Fallback Accuracy', '0.000'),
            ('Weight Performance', '0.000'),
            ('Quality Score', '0.000')
        ]
        
        for i, (label, initial_value) in enumerate(metrics):
            row = i // 5
            col = i % 5
            
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            
            title_label = QLabel(label)
            title_label.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(title_label)
            
            value_label = QLabel(initial_value)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2196F3;")
            frame_layout.addWidget(value_label)
            
            self.metric_labels[label] = value_label
            layout.addWidget(frame, row, col)
        
        return panel
    
    def setup_data_collection(self):
        """Setup data collection thread"""
        self.data_thread = LightweightDataCollectorThread(self.crawler, self.active_metrics)
        self.data_thread.data_ready.connect(self.update_charts)
        self.data_thread.start()
        
        # Setup performance monitoring timer
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance)
        self.performance_timer.start(2000)  # Update every 2 seconds to save CPU
    
    def update_performance(self):
        """Update performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            self.performance_label.setText(f"CPU: {cpu_percent:.1f}% | Memory: {memory_percent:.1f}%")
        except Exception as e:
            logger.error(f"Performance update error: {e}")
    
    def update_charts(self, data):
        """Update current chart with new data"""
        try:
            timestamp = data['timestamp']
            
            # Update only the current chart
            if self.current_chart and self.current_chart in self.charts:
                chart_widget = self.charts[self.current_chart]
                
                if self.current_chart == 'error_metrics':
                    # Update combined error metrics chart
                    rms_value = data.get('rms_error', 0)
                    standard_error_value = data.get('standard_error', 0)
                    chart_widget.update_data(timestamp, rms_value, standard_error_value)
                elif self.current_chart == 'memory_usage':
                    chart_widget.update_data(timestamp, data['memory_usage'] / 100.0)
                else:
                    chart_widget.update_data(timestamp, data.get(self.current_chart, 0))
            
            # Update console
            self.console_widget.update_metrics(data)
            
            # Update metric labels
            self.update_metric_labels(data)
            
        except Exception as e:
            logger.error(f"Chart update error: {e}")
    
    def update_metric_labels(self, data):
        """Update metric labels with current values"""
        self.metric_labels['RMS Error'].setText(f"{data.get('rms_error', 0):.3f}")
        self.metric_labels['Standard Error'].setText(f"{data.get('standard_error', 0):.3f}")
        self.metric_labels['Accuracy'].setText(f"{data.get('classification_accuracy', 0):.3f}")
        self.metric_labels['Confidence'].setText(f"{data.get('confidence_scores', 0):.3f}")
        self.metric_labels['Processing Time'].setText(f"{data.get('processing_time', 0):.3f}s")
        self.metric_labels['Memory Usage'].setText(f"{data.get('memory_usage', 0):.1f}%")
        self.metric_labels['BERT Accuracy'].setText(f"{data.get('bert_accuracy', 0):.3f}")
        self.metric_labels['Fallback Accuracy'].setText(f"{data.get('fallback_accuracy', 0):.3f}")
        self.metric_labels['Weight Performance'].setText(f"{data.get('weight_performance', 0):.3f}")
        self.metric_labels['Quality Score'].setText(f"{data.get('quality_scores', 0):.3f}")
    
    def start_real_crawling(self):
        """Start real crawling with visualization"""
        if self.crawler:
            self.data_thread.set_crawl_active(True)
            self.status_label.setText("Status: Real Crawling Active")
            self.start_button.setEnabled(False)
            self.simulation_button.setEnabled(False)
            logger.info("Started real crawling with live visualization")
        else:
            self.status_label.setText("Status: No crawler available")
            logger.warning("No crawler instance available")
    
    def start_simulation(self):
        """Start simulation mode"""
        self.data_thread.set_crawl_active(False)
        self.status_label.setText("Status: Simulation Active")
        self.start_button.setEnabled(False)
        self.simulation_button.setEnabled(False)
        logger.info("Started simulation mode")
    
    def stop_visualization(self):
        """Stop the visualization"""
        self.data_thread.stop()
        self.status_label.setText("Status: Stopped")
        self.start_button.setEnabled(True)
        self.simulation_button.setEnabled(True)
        logger.info("Visualization stopped")
    
    def reset_current_chart(self):
        """Reset the current chart"""
        if self.current_chart and self.current_chart in self.charts:
            chart_widget = self.charts[self.current_chart]
            chart_widget.reset_chart()
            self.status_label.setText(f"Status: Reset {self.current_chart} chart")
            logger.info(f"Reset {self.current_chart} chart")
    
    def export_data(self):
        """Export metrics data to JSON"""
        try:
            # Collect current data from charts
            export_data = {
                'timestamp': time.time(),
                'charts_data': {}
            }
            
            for name, chart in self.charts.items():
                if hasattr(chart, 'series'):
                    points = chart.series.points()
                    export_data['charts_data'][name] = [
                        {'x': p.x(), 'y': p.y()} for p in points
                    ]
                elif hasattr(chart, 'rms_series'):
                    rms_points = chart.rms_series.points()
                    std_points = chart.standard_error_series.points()
                    export_data['charts_data'][name] = {
                        'rms_error': [{'x': p.x(), 'y': p.y()} for p in rms_points],
                        'standard_error': [{'x': p.x(), 'y': p.y()} for p in std_points]
                    }
            
            filename = f"lightweight_ml_metrics_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.status_label.setText(f"Status: Data exported to {filename}")
            logger.info(f"Metrics data exported to {filename}")
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            self.status_label.setText("Status: Export Failed")
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.data_thread.stop()
        self.data_thread.wait()
        event.accept()

def create_visualization_window(crawler_instance=None):
    """Create and return a visualization window instance"""
    return PySide6LightweightVisualization(crawler_instance)

def main():
    """Main function to run the lightweight PySide6 visualization"""
    print("🚀 Starting PySide6 Lightweight ML Visualization...")
    print("📊 Optimized for low memory usage with 1-second updates")
    
    try:
        # Create application
        app = QApplication(sys.argv)
        
        # Create and show visualization
        viz = PySide6LightweightVisualization()
        viz.show()
        
        print("✅ Lightweight visualization started")
        print("📈 Features:")
        print("   - 1-second updates to reduce memory usage")
        print("   - Simple line charts with connected points")
        print("   - Real crawler data integration")
        print("   - Sliding time window (1-60 seconds)")
        print("\n🎮 Controls:")
        print("   - Tabs: Switch between different metrics")
        print("   - Reset Current Chart: Clear current chart data")
        print("   - Start Real Crawling: Connect to actual crawler")
        print("   - Export Data: Save metrics to JSON file")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Lightweight visualization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 