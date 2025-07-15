import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import os
from datetime import datetime
import threading
import time
from collections import defaultdict, Counter
import numpy as np

class AnalyticsDashboard:
    def __init__(self, port=8080):
        self.app = dash.Dash(__name__)
        self.port = port
        self.data = []
        self.data_lock = threading.Lock()
        self.is_running = False
        
        # Initialize the dashboard layout
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """Setup the dashboard layout"""
        self.app.layout = html.Div([
            html.H1("Earth Engine Crawler Analytics Dashboard", 
                   style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': 30}),
            
            # Summary cards
            html.Div([
                html.Div([
                    html.H3(id='total-datasets', children='0'),
                    html.P('Total Datasets')
                ], className='summary-card'),
                html.Div([
                    html.H3(id='total-providers', children='0'),
                    html.P('Unique Providers')
                ], className='summary-card'),
                html.Div([
                    html.H3(id='avg-confidence', children='0%'),
                    html.P('Avg Confidence')
                ], className='summary-card'),
                html.Div([
                    html.H3(id='ml-classified', children='0'),
                    html.P('ML Classified')
                ], className='summary-card')
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 30}),
            
            # Charts
            html.Div([
                # Top row
                html.Div([
                    dcc.Graph(id='providers-chart', style={'height': 400}),
                    dcc.Graph(id='confidence-distribution', style={'height': 400})
                ], style={'display': 'flex', 'gap': 20}),
                
                # Bottom row
                html.Div([
                    dcc.Graph(id='tags-cloud', style={'height': 400}),
                    dcc.Graph(id='temporal-trend', style={'height': 400})
                ], style={'display': 'flex', 'gap': 20, 'marginTop': 20})
            ]),
            
            # Data table
            html.Div([
                html.H3("Recent Datasets"),
                html.Div(id='datasets-table')
            ], style={'marginTop': 30}),
            
            # Auto-refresh
            dcc.Interval(
                id='interval-component',
                interval=5*1000,  # 5 seconds
                n_intervals=0
            )
        ], style={'padding': 20})
        
        # Add CSS
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Earth Engine Crawler Analytics</title>
                <style>
                    .summary-card {
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        text-align: center;
                        min-width: 150px;
                    }
                    .summary-card h3 {
                        color: #3498db;
                        margin: 0;
                        font-size: 2em;
                    }
                    .summary-card p {
                        color: #7f8c8d;
                        margin: 5px 0 0 0;
                    }
                    body {
                        background-color: #f8f9fa;
                        font-family: Arial, sans-serif;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def setup_callbacks(self):
        """Setup dashboard callbacks"""
        
        @self.app.callback(
            [Output('total-datasets', 'children'),
             Output('total-providers', 'children'),
             Output('avg-confidence', 'children'),
             Output('ml-classified', 'children')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_summary_cards(n):
            with self.data_lock:
                if not self.data:
                    return '0', '0', '0%', '0'
                
                total_datasets = len(self.data)
                providers = set(item.get('provider', 'Unknown') for item in self.data if item.get('provider'))
                total_providers = len(providers)
                
                # Calculate average confidence
                confidences = []
                for item in self.data:
                    if 'confidence' in item and isinstance(item['confidence'], dict):
                        confidences.extend([v for v in item['confidence'].values() if isinstance(v, (int, float))])
                
                avg_confidence = f"{np.mean(confidences):.1f}%" if confidences else "0%"
                
                # Count ML classified items
                ml_classified = sum(1 for item in self.data if item.get('ml_classification'))
                
                return str(total_datasets), str(total_providers), avg_confidence, str(ml_classified)
        
        @self.app.callback(
            Output('providers-chart', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_providers_chart(n):
            with self.data_lock:
                if not self.data:
                    return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                
                providers = [item.get('provider', 'Unknown') for item in self.data if item.get('provider')]
                provider_counts = Counter(providers)
                
                fig = px.bar(
                    x=list(provider_counts.keys()),
                    y=list(provider_counts.values()),
                    title="Datasets by Provider",
                    labels={'x': 'Provider', 'y': 'Count'}
                )
                fig.update_layout(showlegend=False)
                return fig
        
        @self.app.callback(
            Output('confidence-distribution', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_confidence_distribution(n):
            with self.data_lock:
                if not self.data:
                    return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                
                confidences = []
                for item in self.data:
                    if 'confidence' in item and isinstance(item['confidence'], dict):
                        confidences.extend([v for v in item['confidence'].values() if isinstance(v, (int, float))])
                
                if not confidences:
                    return go.Figure().add_annotation(text="No confidence data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                
                fig = px.histogram(
                    x=confidences,
                    title="Confidence Score Distribution",
                    labels={'x': 'Confidence Score', 'y': 'Count'},
                    nbins=20
                )
                return fig
        
        @self.app.callback(
            Output('tags-cloud', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_tags_cloud(n):
            with self.data_lock:
                if not self.data:
                    return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                
                all_tags = []
                for item in self.data:
                    if 'tags' in item and isinstance(item['tags'], list):
                        all_tags.extend(item['tags'])
                
                if not all_tags:
                    return go.Figure().add_annotation(text="No tags data", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                
                tag_counts = Counter(all_tags)
                top_tags = dict(tag_counts.most_common(20))
                
                fig = px.bar(
                    x=list(top_tags.keys()),
                    y=list(top_tags.values()),
                    title="Top Tags",
                    labels={'x': 'Tag', 'y': 'Count'}
                )
                fig.update_xaxes(tickangle=45)
                return fig
        
        @self.app.callback(
            Output('temporal-trend', 'figure'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_temporal_trend(n):
            with self.data_lock:
                if not self.data:
                    return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
                
                # Group by extraction time (simplified - using current time for demo)
                current_time = datetime.now()
                fig = px.scatter(
                    x=[current_time] * len(self.data),
                    y=range(len(self.data)),
                    title="Dataset Extraction Timeline",
                    labels={'x': 'Time', 'y': 'Dataset Index'}
                )
                return fig
        
        @self.app.callback(
            Output('datasets-table', 'children'),
            [Input('interval-component', 'n_intervals')]
        )
        def update_datasets_table(n):
            with self.data_lock:
                if not self.data:
                    return html.P("No datasets available")
                
                # Show last 10 datasets
                recent_data = self.data[-10:]
                
                table_rows = []
                for item in recent_data:
                    title = item.get('title', 'No title')[:50] + '...' if len(item.get('title', '')) > 50 else item.get('title', 'No title')
                    provider = item.get('provider', 'Unknown')
                    confidence = item.get('confidence', {})
                    avg_conf = np.mean([v for v in confidence.values() if isinstance(v, (int, float))]) if confidence else 0
                    
                    table_rows.append(html.Tr([
                        html.Td(title),
                        html.Td(provider),
                        html.Td(f"{avg_conf:.1f}%"),
                        html.Td("✅" if item.get('ml_classification') else "❌")
                    ]))
                
                return html.Table([
                    html.Thead(html.Tr([
                        html.Th("Title"),
                        html.Th("Provider"),
                        html.Th("Confidence"),
                        html.Th("ML Classified")
                    ])),
                    html.Tbody(table_rows)
                ], style={'width': '100%', 'borderCollapse': 'collapse'})
    
    def add_data(self, data_item):
        """Add a single data item to the dashboard"""
        with self.data_lock:
            # Add timestamp if not present
            if 'extraction_time' not in data_item:
                data_item['extraction_time'] = datetime.now().isoformat()
            
            self.data.append(data_item)
            
            # Keep only last 1000 items to prevent memory issues
            if len(self.data) > 1000:
                self.data = self.data[-1000:]
    
    def add_batch_data(self, data_items):
        """Add multiple data items to the dashboard"""
        with self.data_lock:
            for item in data_items:
                if 'extraction_time' not in item:
                    item['extraction_time'] = datetime.now().isoformat()
                self.data.append(item)
            
            # Keep only last 1000 items
            if len(self.data) > 1000:
                self.data = self.data[-1000:]
    
    def start_background(self):
        """Start the dashboard in background thread"""
        if not self.is_running:
            self.is_running = True
            thread = threading.Thread(target=self._run_server, daemon=True)
            thread.start()
            return True
        return False
    
    def _run_server(self):
        """Run the Dash server"""
        try:
            self.app.run(debug=False, host='127.0.0.1', port=self.port)
        except Exception as e:
            print(f"Dashboard server error: {e}")
            self.is_running = False
    
    def get_data(self):
        """Get current data (thread-safe)"""
        with self.data_lock:
            return self.data.copy()
    
    def clear_data(self):
        """Clear all data"""
        with self.data_lock:
            self.data = []

def get_dashboard():
    """Factory function to create and return a dashboard instance"""
    return AnalyticsDashboard()

if __name__ == "__main__":
    # Test the dashboard
    dashboard = AnalyticsDashboard()
    dashboard.start_background()
    print("Dashboard started on http://127.0.0.1:8080")
    
    # Add some test data
    test_data = [
        {
            'title': 'Test Dataset 1',
            'provider': 'NASA',
            'confidence': {'title': 0.9, 'description': 0.8},
            'tags': ['satellite', 'landsat'],
            'ml_classification': {'bert': {'label': 'satellite_data', 'confidence': 0.85}}
        },
        {
            'title': 'Test Dataset 2',
            'provider': 'ESA',
            'confidence': {'title': 0.95, 'description': 0.9},
            'tags': ['optical', 'sentinel'],
            'ml_classification': {'bert': {'label': 'optical_data', 'confidence': 0.92}}
        }
    ]
    
    dashboard.add_batch_data(test_data)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Dashboard stopped") 