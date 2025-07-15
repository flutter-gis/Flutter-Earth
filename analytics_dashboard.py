import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import threading
import time
import psutil
import os
from collections import defaultdict, deque
from datetime import datetime

class AnalyticsDashboard:
    def __init__(self, port=8080):
        self.app = dash.Dash(__name__)
        self.port = port
        self.data = []
        self.stats = defaultdict(int)
        
        # Memory monitoring data - simplified
        self.memory_history = deque(maxlen=50)  # Reduced size
        self.cpu_history = deque(maxlen=50)     # Reduced size
        self.process_info = {}
        self.monitoring_active = False
        
        self.setup_layout()
        self.setup_callbacks()
        # Don't start monitoring automatically - will start when needed
        
    def start_memory_monitoring(self):
        """Start background memory monitoring thread."""
        if not self.monitoring_active:
            self.monitoring_active = True
            monitor_thread = threading.Thread(target=self.memory_monitor_loop, daemon=True)
            monitor_thread.start()
        
    def memory_monitor_loop(self):
        """Background loop to monitor system resources."""
        while self.monitoring_active:
            try:
                # Get system memory info
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=0.1)  # Reduced interval
                
                # Get process info for crawler
                crawler_process = self.find_crawler_process()
                process_info = {}
                
                if crawler_process:
                    try:
                        process_info = {
                            'pid': crawler_process.pid,
                            'memory_mb': crawler_process.memory_info().rss / 1024 / 1024,
                            'cpu_percent': crawler_process.cpu_percent(),
                            'status': crawler_process.status(),
                            'create_time': datetime.fromtimestamp(crawler_process.create_time()).strftime('%H:%M:%S'),
                            'num_threads': crawler_process.num_threads(),
                            'memory_percent': crawler_process.memory_percent()
                        }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_info = {'error': 'Process not accessible'}
                
                # Store monitoring data
                timestamp = datetime.now()
                self.memory_history.append({
                    'timestamp': timestamp,
                    'system_memory_percent': memory.percent,
                    'system_memory_used_gb': memory.used / 1024 / 1024 / 1024,
                    'system_memory_total_gb': memory.total / 1024 / 1024 / 1024,
                    'cpu_percent': cpu_percent,
                    'process_memory_mb': process_info.get('memory_mb', 0),
                    'process_cpu_percent': process_info.get('cpu_percent', 0),
                    'process_status': process_info.get('status', 'Unknown')
                })
                
                self.cpu_history.append({
                    'timestamp': timestamp,
                    'cpu_percent': cpu_percent
                })
                
                self.process_info = process_info
                
            except Exception as e:
                print(f"Memory monitoring error: {e}")
            
            time.sleep(3)  # Increased interval to reduce load
    
    def find_crawler_process(self):
        """Find the crawler UI process."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if proc.info['name'] == 'python.exe':
                        cmdline = proc.info['cmdline']
                        if cmdline and any('enhanced_crawler_ui.py' in arg for arg in cmdline):
                            return proc
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error finding crawler process: {e}")
        return None
        
    def setup_layout(self):
        """Setup the dashboard layout with charts and controls."""
        self.app.layout = html.Div([
            html.H1("Earth Engine Crawler Analytics Dashboard", 
                   style={'textAlign': 'center', 'color': '#2c3e50'}),
            
            # Real-time statistics row
            html.Div([
                html.Div([
                    html.H3("Total Datasets", id="total-datasets"),
                    html.H2("0", id="total-datasets-value", style={'color': '#3498db'})
                ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'}),
                html.Div([
                    html.H3("Avg Quality Score", id="avg-quality"),
                    html.H2("0", id="avg-quality-value", style={'color': '#e74c3c'})
                ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'}),
                html.Div([
                    html.H3("Success Rate", id="success-rate"),
                    html.H2("0%", id="success-rate-value", style={'color': '#27ae60'})
                ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'}),
                html.Div([
                    html.H3("ML Confidence", id="ml-confidence"),
                    html.H2("0", id="ml-confidence-value", style={'color': '#f39c12'})
                ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'})
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
            
            # Memory monitoring section
            html.Div([
                html.H2("System Resource Monitoring", 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginTop': '30px'}),
                
                # System resource stats
                html.Div([
                    html.Div([
                        html.H3("System Memory", id="system-memory"),
                        html.H2("0%", id="system-memory-value", style={'color': '#e74c3c'})
                    ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'}),
                    html.Div([
                        html.H3("System CPU", id="system-cpu"),
                        html.H2("0%", id="system-cpu-value", style={'color': '#f39c12'})
                    ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'}),
                    html.Div([
                        html.H3("Crawler Memory", id="crawler-memory"),
                        html.H2("0 MB", id="crawler-memory-value", style={'color': '#3498db'})
                    ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'}),
                    html.Div([
                        html.H3("Crawler CPU", id="crawler-cpu"),
                        html.H2("0%", id="crawler-cpu-value", style={'color': '#27ae60'})
                    ], style={'background': 'white', 'border': '1px solid #ddd', 'borderRadius': '8px', 'padding': '15px', 'margin': '10px', 'textAlign': 'center', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'minWidth': '150px'})
                ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
                
                # Memory and CPU charts
                html.Div([
                    html.Div([
                        html.H3("Memory Usage Over Time"),
                        dcc.Graph(id="memory-chart")
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    
                    html.Div([
                        html.H3("CPU Usage Over Time"),
                        dcc.Graph(id="cpu-chart")
                    ], style={'width': '50%', 'display': 'inline-block'})
                ]),
                
                # Process details
                html.Div([
                    html.H3("Crawler Process Details"),
                    html.Div(id="process-details")
                ], style={'margin': '20px', 'padding': '15px', 'border': '1px solid #ddd', 'borderRadius': '5px'})
            ]),
            
            # Charts row
            html.Div([
                # Field extraction success chart
                html.Div([
                    html.H3("Field Extraction Success Rate"),
                    dcc.Graph(id="field-success-chart")
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                # ML classification distribution
                html.Div([
                    html.H3("ML Classification Distribution"),
                    dcc.Graph(id="ml-classification-chart")
                ], style={'width': '50%', 'display': 'inline-block'})
            ]),
            
            # Quality score distribution
            html.Div([
                html.H3("Data Quality Score Distribution"),
                dcc.Graph(id="quality-distribution-chart")
            ]),
            
            # Real-time data table
            html.Div([
                html.H3("Recent Extractions"),
                html.Div(id="recent-data-table")
            ]),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # 5 seconds - increased to reduce load
                n_intervals=0
            )
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks for real-time updates."""
        
        @self.app.callback(
            [Output("total-datasets-value", "children"),
             Output("avg-quality-value", "children"),
             Output("success-rate-value", "children"),
             Output("ml-confidence-value", "children"),
             Output("system-memory-value", "children"),
             Output("system-cpu-value", "children"),
             Output("crawler-memory-value", "children"),
             Output("crawler-cpu-value", "children")],
            [Input("interval-component", "n_intervals")]
        )
        def update_stats(n):
            # Start memory monitoring if not already started
            if not self.monitoring_active:
                self.start_memory_monitoring()
            
            # Crawler data stats
            if not self.data:
                total, avg_quality, success_rate, avg_ml_conf = "0", "0", "0%", "0"
            else:
                total = len(self.data)
                quality_scores = [d.get('data_quality_score', 0) for d in self.data]
                avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
                
                # Calculate success rate (datasets with title and description)
                successful = sum(1 for d in self.data if d.get('title') and d.get('description'))
                success_rate = (successful / total * 100) if total > 0 else 0
                
                # Average ML confidence
                ml_confidences = []
                for d in self.data:
                    for ml_info in d.get('ml_classification', {}).values():
                        if isinstance(ml_info, dict) and 'confidence' in ml_info:
                            ml_confidences.append(ml_info['confidence'])
                avg_ml_conf = sum(ml_confidences) / len(ml_confidences) if ml_confidences else 0
                
                total, avg_quality, success_rate, avg_ml_conf = str(total), f"{avg_quality:.1f}", f"{success_rate:.1f}%", f"{avg_ml_conf:.2f}"
            
            # System resource stats - with error handling
            try:
                if self.memory_history:
                    latest = self.memory_history[-1]
                    system_memory = f"{latest['system_memory_percent']:.1f}%"
                    system_cpu = f"{latest['cpu_percent']:.1f}%"
                    crawler_memory = f"{latest['process_memory_mb']:.1f} MB"
                    crawler_cpu = f"{latest['process_cpu_percent']:.1f}%"
                else:
                    # Get current system stats if no history
                    memory = psutil.virtual_memory()
                    system_memory = f"{memory.percent:.1f}%"
                    system_cpu = f"{psutil.cpu_percent():.1f}%"
                    crawler_memory = "0 MB"
                    crawler_cpu = "0%"
            except Exception as e:
                print(f"Error getting system stats: {e}")
                system_memory, system_cpu, crawler_memory, crawler_cpu = "0%", "0%", "0 MB", "0%"
            
            return total, avg_quality, success_rate, avg_ml_conf, system_memory, system_cpu, crawler_memory, crawler_cpu
        
        @self.app.callback(
            Output("field-success-chart", "figure"),
            [Input("interval-component", "n_intervals")]
        )
        def update_field_success_chart(n):
            if not self.data:
                return go.Figure()
            
            fields = ['title', 'description', 'provider', 'tags', 'date_range', 'bands']
            success_rates = []
            
            for field in fields:
                successful = sum(1 for d in self.data if d.get(field))
                rate = (successful / len(self.data) * 100) if self.data else 0
                success_rates.append(rate)
            
            fig = px.bar(
                x=fields, 
                y=success_rates,
                title="Field Extraction Success Rate (%)",
                labels={'x': 'Fields', 'y': 'Success Rate (%)'}
            )
            fig.update_traces(marker_color='#3498db')
            return fig
        
        @self.app.callback(
            Output("ml-classification-chart", "figure"),
            [Input("interval-component", "n_intervals")]
        )
        def update_ml_classification_chart(n):
            if not self.data:
                return go.Figure()
            
            ml_labels = defaultdict(int)
            for d in self.data:
                for ml_info in d.get('ml_classification', {}).values():
                    if isinstance(ml_info, dict) and 'label' in ml_info:
                        ml_labels[ml_info['label']] += 1
            
            if not ml_labels:
                return go.Figure()
            
            fig = px.pie(
                values=list(ml_labels.values()),
                names=list(ml_labels.keys()),
                title="ML Classification Distribution"
            )
            return fig
        
        @self.app.callback(
            Output("quality-distribution-chart", "figure"),
            [Input("interval-component", "n_intervals")]
        )
        def update_quality_distribution_chart(n):
            if not self.data:
                return go.Figure()
            
            quality_scores = [d.get('data_quality_score', 0) for d in self.data]
            
            fig = px.histogram(
                x=quality_scores,
                nbins=20,
                title="Data Quality Score Distribution",
                labels={'x': 'Quality Score', 'y': 'Count'}
            )
            fig.update_traces(marker_color='#e74c3c')
            return fig
        
        @self.app.callback(
            Output("memory-chart", "figure"),
            [Input("interval-component", "n_intervals")]
        )
        def update_memory_chart(n):
            try:
                if not self.memory_history or len(self.memory_history) < 2:
                    # Return empty figure if not enough data
                    return go.Figure().add_annotation(
                        text="Waiting for memory data...",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                
                # Prepare data for plotting
                timestamps = [entry['timestamp'] for entry in self.memory_history]
                system_memory = [entry['system_memory_percent'] for entry in self.memory_history]
                process_memory = [entry['process_memory_mb'] for entry in self.memory_history]
                
                fig = go.Figure()
                
                # System memory line
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=system_memory,
                    mode='lines+markers',
                    name='System Memory %',
                    line=dict(color='#e74c3c', width=2),
                    marker=dict(size=4)
                ))
                
                # Process memory line
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=process_memory,
                    mode='lines+markers',
                    name='Crawler Memory (MB)',
                    line=dict(color='#3498db', width=2),
                    marker=dict(size=4),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title="Memory Usage Over Time",
                    xaxis_title="Time",
                    yaxis_title="System Memory (%)",
                    yaxis2=dict(
                        title="Process Memory (MB)",
                        overlaying='y',
                        side='right'
                    ),
                    hovermode='x unified',
                    height=400
                )
                
                return fig
            except Exception as e:
                print(f"Error updating memory chart: {e}")
                return go.Figure().add_annotation(
                    text="Error loading memory chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
        
        @self.app.callback(
            Output("cpu-chart", "figure"),
            [Input("interval-component", "n_intervals")]
        )
        def update_cpu_chart(n):
            try:
                if not self.cpu_history or len(self.cpu_history) < 2:
                    # Return empty figure if not enough data
                    return go.Figure().add_annotation(
                        text="Waiting for CPU data...",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                
                # Prepare data for plotting
                timestamps = [entry['timestamp'] for entry in self.cpu_history]
                cpu_percent = [entry['cpu_percent'] for entry in self.cpu_history]
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=cpu_percent,
                    mode='lines+markers',
                    name='CPU Usage %',
                    line=dict(color='#f39c12', width=2),
                    marker=dict(size=4),
                    fill='tonexty'
                ))
                
                fig.update_layout(
                    title="CPU Usage Over Time",
                    xaxis_title="Time",
                    yaxis_title="CPU Usage (%)",
                    hovermode='x unified',
                    height=400
                )
                
                return fig
            except Exception as e:
                print(f"Error updating CPU chart: {e}")
                return go.Figure().add_annotation(
                    text="Error loading CPU chart",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, showarrow=False
                )
        
        @self.app.callback(
            Output("process-details", "children"),
            [Input("interval-component", "n_intervals")]
        )
        def update_process_details(n):
            if not self.process_info or 'error' in self.process_info:
                return html.Div([
                    html.P("⚠ Crawler process not found or not accessible", 
                           style={'color': '#e74c3c', 'fontWeight': 'bold'}),
                    html.P("Make sure enhanced_crawler_ui.py is running")
                ])
            
            return html.Div([
                html.Div([
                    html.Strong("Process ID: "), html.Span(f"{self.process_info.get('pid', 'N/A')}"),
                    html.Br(),
                    html.Strong("Status: "), html.Span(self.process_info.get('status', 'N/A')),
                    html.Br(),
                    html.Strong("Created: "), html.Span(self.process_info.get('create_time', 'N/A')),
                    html.Br(),
                    html.Strong("Threads: "), html.Span(f"{self.process_info.get('num_threads', 'N/A')}"),
                    html.Br(),
                    html.Strong("Memory: "), html.Span(f"{self.process_info.get('memory_mb', 0):.1f} MB"),
                    html.Br(),
                    html.Strong("Memory %: "), html.Span(f"{self.process_info.get('memory_percent', 0):.1f}%"),
                    html.Br(),
                    html.Strong("CPU %: "), html.Span(f"{self.process_info.get('cpu_percent', 0):.1f}%")
                ], style={'fontFamily': 'monospace', 'lineHeight': '1.6'})
            ])
        
        @self.app.callback(
            Output("recent-data-table", "children"),
            [Input("interval-component", "n_intervals")]
        )
        def update_recent_data_table(n):
            if not self.data:
                return html.P("No data available")
            
            # Show last 10 datasets
            recent_data = self.data[-10:]
            
            table_rows = []
            for i, data in enumerate(reversed(recent_data)):
                title = data.get('title', 'N/A')[:50]
                quality = data.get('data_quality_score', 0)
                fields_found = len([f for f in data.keys() if data.get(f) and f not in ['extraction_report', 'confidence', 'ml_classification', 'validation_results']])
                
                row = html.Tr([
                    html.Td(f"{len(self.data) - i}"),
                    html.Td(title),
                    html.Td(f"{quality:.1f}"),
                    html.Td(fields_found)
                ])
                table_rows.append(row)
            
            return html.Table([
                html.Thead([
                    html.Tr([
                        html.Th("ID"),
                        html.Th("Title"),
                        html.Th("Quality"),
                        html.Th("Fields")
                    ])
                ]),
                html.Tbody(table_rows)
            ])
    
    def add_data(self, dataset_data):
        """Add new dataset data to the dashboard."""
        self.data.append(dataset_data)
        
        # Update statistics
        self.stats['total_datasets'] += 1
        if dataset_data.get('title'):
            self.stats['with_title'] += 1
        if dataset_data.get('description'):
            self.stats['with_description'] += 1
    
    def start(self):
        """Start the dashboard server."""
        self.app.run(debug=False, port=self.port, host='127.0.0.1')
    
    def start_background(self):
        """Start the dashboard in a background thread."""
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop the memory monitoring."""
        self.monitoring_active = False
    
    def __del__(self):
        """Cleanup when dashboard is destroyed."""
        self.stop_monitoring()

# Global dashboard instance
dashboard = None

def get_dashboard():
    """Get or create the global dashboard instance."""
    global dashboard
    if dashboard is None:
        dashboard = AnalyticsDashboard()
    return dashboard 