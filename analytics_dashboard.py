import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import threading
import time
from collections import defaultdict

class AnalyticsDashboard:
    def __init__(self, port=8080):
        self.app = dash.Dash(__name__)
        self.port = port
        self.data = []
        self.stats = defaultdict(int)
        self.setup_layout()
        self.setup_callbacks()
        
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
                ], className="stat-card"),
                html.Div([
                    html.H3("Avg Quality Score", id="avg-quality"),
                    html.H2("0", id="avg-quality-value", style={'color': '#e74c3c'})
                ], className="stat-card"),
                html.Div([
                    html.H3("Success Rate", id="success-rate"),
                    html.H2("0%", id="success-rate-value", style={'color': '#27ae60'})
                ], className="stat-card"),
                html.Div([
                    html.H3("ML Confidence", id="ml-confidence"),
                    html.H2("0", id="ml-confidence-value", style={'color': '#f39c12'})
                ], className="stat-card")
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
            
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
                interval=2*1000,  # 2 seconds
                n_intervals=0
            )
        ])
    
    def setup_callbacks(self):
        """Setup dashboard callbacks for real-time updates."""
        
        @self.app.callback(
            [Output("total-datasets-value", "children"),
             Output("avg-quality-value", "children"),
             Output("success-rate-value", "children"),
             Output("ml-confidence-value", "children")],
            [Input("interval-component", "n_intervals")]
        )
        def update_stats(n):
            if not self.data:
                return "0", "0", "0%", "0"
            
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
            
            return str(total), f"{avg_quality:.1f}", f"{success_rate:.1f}%", f"{avg_ml_conf:.2f}"
        
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

# Global dashboard instance
dashboard = None

def get_dashboard():
    """Get or create the global dashboard instance."""
    global dashboard
    if dashboard is None:
        dashboard = AnalyticsDashboard()
    return dashboard 