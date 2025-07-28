#!/usr/bin/env python3
"""
Advanced Data Explorer and Visualization System
Interactive data exploration with AI-powered insights and 3D visualizations
"""

import os
import json
import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import hashlib
import sqlite3

# Visualization imports
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

# Data processing
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Geospatial
try:
    import folium
    from folium import plugins
    FOLIUM_AVAILABLE = True
except ImportError:
    FOLIUM_AVAILABLE = False

# AI/ML for insights
try:
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

@dataclass
class VisualizationConfig:
    """Configuration for data visualizations"""
    chart_type: str  # 'scatter', 'bar', 'line', '3d', 'map', 'heatmap', 'network'
    data_source: str
    x_axis: str
    y_axis: str
    z_axis: Optional[str] = None
    color_by: Optional[str] = None
    size_by: Optional[str] = None
    filters: Dict[str, Any] = None
    animation_frame: Optional[str] = None
    layout_config: Dict[str, Any] = None

@dataclass
class InsightResult:
    """AI-powered insight result"""
    insight_type: str  # 'pattern', 'anomaly', 'trend', 'correlation', 'cluster'
    title: str
    description: str
    confidence: float
    data_points: List[Dict[str, Any]]
    visualization_config: Optional[VisualizationConfig] = None
    timestamp: datetime = None

class AdvancedDataExplorer:
    """Advanced data exploration and visualization system"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Data storage
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.visualizations: Dict[str, Any] = {}
        self.insights: List[InsightResult] = []
        
        # Cache for performance
        self.cache_dir = "explorer_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize visualization engines
        self._init_visualization_engines()
        
        # Background processing
        self.insight_thread = threading.Thread(target=self._background_insight_generation, daemon=True)
        self.insight_thread.start()
    
    def _init_visualization_engines(self):
        """Initialize visualization engines"""
        self.engines = {}
        
        if PLOTLY_AVAILABLE:
            self.engines['plotly'] = True
        
        if MATPLOTLIB_AVAILABLE:
            self.engines['matplotlib'] = True
        
        if SEABORN_AVAILABLE:
            self.engines['seaborn'] = True
        
        if FOLIUM_AVAILABLE:
            self.engines['folium'] = True
    
    def load_dataset(self, dataset_id: str, data: Union[pd.DataFrame, List[Dict[str, Any]]]) -> bool:
        """Load dataset for exploration"""
        try:
            if isinstance(data, list):
                df = pd.DataFrame(data)
            else:
                df = data.copy()
            
            # Clean and preprocess data
            df = self._preprocess_data(df)
            
            self.datasets[dataset_id] = df
            self.logger.info(f"Loaded dataset {dataset_id} with {len(df)} rows")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading dataset {dataset_id}: {e}")
            return False
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data for exploration"""
        # Handle missing values
        df = df.fillna('Unknown')
        
        # Convert date columns
        date_columns = df.select_dtypes(include=['object']).columns
        for col in date_columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
        
        # Extract numeric columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            # Handle outliers
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers
            df[col] = df[col].clip(lower_bound, upper_bound)
        
        return df
    
    def create_visualization(self, dataset_id: str, config: VisualizationConfig) -> Optional[str]:
        """Create visualization based on configuration"""
        if dataset_id not in self.datasets:
            self.logger.error(f"Dataset {dataset_id} not found")
            return None
        
        df = self.datasets[dataset_id]
        viz_id = f"{dataset_id}_{config.chart_type}_{hash(str(config))}"
        
        try:
            if config.chart_type == 'scatter':
                viz = self._create_scatter_plot(df, config)
            elif config.chart_type == 'bar':
                viz = self._create_bar_chart(df, config)
            elif config.chart_type == 'line':
                viz = self._create_line_chart(df, config)
            elif config.chart_type == '3d':
                viz = self._create_3d_plot(df, config)
            elif config.chart_type == 'map':
                viz = self._create_map_visualization(df, config)
            elif config.chart_type == 'heatmap':
                viz = self._create_heatmap(df, config)
            elif config.chart_type == 'network':
                viz = self._create_network_graph(df, config)
            else:
                self.logger.error(f"Unknown chart type: {config.chart_type}")
                return None
            
            self.visualizations[viz_id] = viz
            return viz_id
            
        except Exception as e:
            self.logger.error(f"Error creating visualization: {e}")
            return None
    
    def _create_scatter_plot(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create scatter plot visualization"""
        if not PLOTLY_AVAILABLE:
            return None
        
        fig = px.scatter(
            df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            size=config.size_by,
            animation_frame=config.animation_frame,
            title=f"Scatter Plot: {config.x_axis} vs {config.y_axis}"
        )
        
        if config.layout_config:
            fig.update_layout(**config.layout_config)
        
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create bar chart visualization"""
        if not PLOTLY_AVAILABLE:
            return None
        
        # Aggregate data if needed
        if config.color_by:
            agg_df = df.groupby([config.x_axis, config.color_by])[config.y_axis].mean().reset_index()
        else:
            agg_df = df.groupby(config.x_axis)[config.y_axis].mean().reset_index()
        
        fig = px.bar(
            agg_df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            title=f"Bar Chart: {config.y_axis} by {config.x_axis}"
        )
        
        if config.layout_config:
            fig.update_layout(**config.layout_config)
        
        return fig
    
    def _create_line_chart(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create line chart visualization"""
        if not PLOTLY_AVAILABLE:
            return None
        
        fig = px.line(
            df,
            x=config.x_axis,
            y=config.y_axis,
            color=config.color_by,
            title=f"Line Chart: {config.y_axis} over {config.x_axis}"
        )
        
        if config.layout_config:
            fig.update_layout(**config.layout_config)
        
        return fig
    
    def _create_3d_plot(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create 3D visualization"""
        if not PLOTLY_AVAILABLE or not config.z_axis:
            return None
        
        fig = px.scatter_3d(
            df,
            x=config.x_axis,
            y=config.y_axis,
            z=config.z_axis,
            color=config.color_by,
            size=config.size_by,
            title=f"3D Plot: {config.x_axis} vs {config.y_axis} vs {config.z_axis}"
        )
        
        if config.layout_config:
            fig.update_layout(**config.layout_config)
        
        return fig
    
    def _create_map_visualization(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create map visualization"""
        if not FOLIUM_AVAILABLE:
            return None
        
        # Check if we have coordinates
        lat_col = config.x_axis if 'lat' in config.x_axis.lower() else None
        lon_col = config.y_axis if 'lon' in config.y_axis.lower() else None
        
        if not lat_col or not lon_col:
            self.logger.warning("Map visualization requires latitude and longitude columns")
            return None
        
        # Create map
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
        
        # Add markers
        for idx, row in df.iterrows():
            folium.Marker(
                [row[lat_col], row[lon_col]],
                popup=row.get(config.color_by, ''),
                tooltip=row.get(config.color_by, '')
            ).add_to(m)
        
        return m
    
    def _create_heatmap(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create heatmap visualization"""
        if not PLOTLY_AVAILABLE:
            return None
        
        # Create pivot table for heatmap
        pivot_df = df.pivot_table(
            values=config.y_axis,
            index=config.x_axis,
            columns=config.color_by,
            aggfunc='mean'
        )
        
        fig = px.imshow(
            pivot_df,
            title=f"Heatmap: {config.y_axis} by {config.x_axis} and {config.color_by}",
            aspect='auto'
        )
        
        if config.layout_config:
            fig.update_layout(**config.layout_config)
        
        return fig
    
    def _create_network_graph(self, df: pd.DataFrame, config: VisualizationConfig) -> Any:
        """Create network graph visualization"""
        if not PLOTLY_AVAILABLE:
            return None
        
        # This is a simplified network graph
        # In a real implementation, you'd use networkx for graph analysis
        
        fig = go.Figure(data=[go.Scatter(
            x=df[config.x_axis],
            y=df[config.y_axis],
            mode='markers+text',
            text=df[config.color_by] if config.color_by else None,
            marker=dict(size=10)
        )])
        
        fig.update_layout(
            title=f"Network Graph: {config.x_axis} vs {config.y_axis}",
            xaxis_title=config.x_axis,
            yaxis_title=config.y_axis
        )
        
        return fig
    
    def generate_insights(self, dataset_id: str) -> List[InsightResult]:
        """Generate AI-powered insights from dataset"""
        if dataset_id not in self.datasets:
            return []
        
        df = self.datasets[dataset_id]
        insights = []
        
        try:
            # Pattern detection
            pattern_insights = self._detect_patterns(df)
            insights.extend(pattern_insights)
            
            # Anomaly detection
            anomaly_insights = self._detect_anomalies(df)
            insights.extend(anomaly_insights)
            
            # Trend analysis
            trend_insights = self._detect_trends(df)
            insights.extend(trend_insights)
            
            # Correlation analysis
            correlation_insights = self._detect_correlations(df)
            insights.extend(correlation_insights)
            
            # Clustering analysis
            cluster_insights = self._detect_clusters(df)
            insights.extend(cluster_insights)
            
            # Store insights
            self.insights.extend(insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return []
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[InsightResult]:
        """Detect patterns in data"""
        insights = []
        
        # Detect temporal patterns
        date_columns = df.select_dtypes(include=['datetime64']).columns
        for col in date_columns:
            if len(df[col].dropna()) > 10:
                # Check for seasonal patterns
                df_temp = df.copy()
                df_temp['month'] = df_temp[col].dt.month
                df_temp['year'] = df_temp[col].dt.year
                
                monthly_counts = df_temp.groupby('month').size()
                if monthly_counts.std() > monthly_counts.mean() * 0.3:
                    insights.append(InsightResult(
                        insight_type='pattern',
                        title='Seasonal Pattern Detected',
                        description=f'Strong seasonal variation detected in {col}',
                        confidence=0.8,
                        data_points=[{'month': m, 'count': c} for m, c in monthly_counts.items()],
                        timestamp=datetime.now()
                    ))
        
        return insights
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[InsightResult]:
        """Detect anomalies in data"""
        insights = []
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if len(df[col].dropna()) > 10:
                # Use IQR method for anomaly detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                anomalies = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                
                if len(anomalies) > 0:
                    insights.append(InsightResult(
                        insight_type='anomaly',
                        title=f'Anomalies Detected in {col}',
                        description=f'Found {len(anomalies)} anomalies in {col}',
                        confidence=0.7,
                        data_points=anomalies.to_dict('records'),
                        timestamp=datetime.now()
                    ))
        
        return insights
    
    def _detect_trends(self, df: pd.DataFrame) -> List[InsightResult]:
        """Detect trends in data"""
        insights = []
        
        # Detect trends in numeric columns over time
        date_columns = df.select_dtypes(include=['datetime64']).columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        for date_col in date_columns:
            for num_col in numeric_columns:
                if len(df[date_col].dropna()) > 10:
                    # Sort by date and calculate trend
                    df_temp = df[[date_col, num_col]].dropna().sort_values(date_col)
                    
                    if len(df_temp) > 5:
                        # Simple linear trend calculation
                        x = np.arange(len(df_temp))
                        y = df_temp[num_col].values
                        
                        if len(y) > 1:
                            slope = np.polyfit(x, y, 1)[0]
                            
                            if abs(slope) > y.std() * 0.1:  # Significant trend
                                trend_direction = 'increasing' if slope > 0 else 'decreasing'
                                insights.append(InsightResult(
                                    insight_type='trend',
                                    title=f'{trend_direction.title()} Trend in {num_col}',
                                    description=f'Detected {trend_direction} trend in {num_col} over time',
                                    confidence=0.6,
                                    data_points=[{'date': str(d), 'value': v} for d, v in zip(df_temp[date_col], df_temp[num_col])],
                                    timestamp=datetime.now()
                                ))
        
        return insights
    
    def _detect_correlations(self, df: pd.DataFrame) -> List[InsightResult]:
        """Detect correlations between variables"""
        insights = []
        
        if not SKLEARN_AVAILABLE:
            return insights
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) >= 2:
            # Calculate correlation matrix
            corr_matrix = df[numeric_columns].corr()
            
            # Find strong correlations
            for i in range(len(numeric_columns)):
                for j in range(i+1, len(numeric_columns)):
                    col1 = numeric_columns[i]
                    col2 = numeric_columns[j]
                    correlation = corr_matrix.iloc[i, j]
                    
                    if abs(correlation) > 0.7:  # Strong correlation
                        correlation_type = 'positive' if correlation > 0 else 'negative'
                        insights.append(InsightResult(
                            insight_type='correlation',
                            title=f'Strong {correlation_type} correlation',
                            description=f'Strong {correlation_type} correlation ({correlation:.2f}) between {col1} and {col2}',
                            confidence=abs(correlation),
                            data_points=[{'variable1': col1, 'variable2': col2, 'correlation': correlation}],
                            timestamp=datetime.now()
                        ))
        
        return insights
    
    def _detect_clusters(self, df: pd.DataFrame) -> List[InsightResult]:
        """Detect clusters in data"""
        insights = []
        
        if not SKLEARN_AVAILABLE:
            return insights
        
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_columns) >= 2:
            # Prepare data for clustering
            data = df[numeric_columns].dropna()
            
            if len(data) > 10:
                # Standardize data
                scaler = StandardScaler()
                data_scaled = scaler.fit_transform(data)
                
                # Apply K-means clustering
                kmeans = KMeans(n_clusters=min(5, len(data)//10), random_state=42)
                clusters = kmeans.fit_predict(data_scaled)
                
                # Add cluster labels to data
                data_with_clusters = data.copy()
                data_with_clusters['cluster'] = clusters
                
                insights.append(InsightResult(
                    insight_type='cluster',
                    title=f'Data Clustering Analysis',
                    description=f'Detected {len(set(clusters))} distinct clusters in the data',
                    confidence=0.7,
                    data_points=data_with_clusters.to_dict('records'),
                    timestamp=datetime.now()
                ))
        
        return insights
    
    def _background_insight_generation(self):
        """Background thread for generating insights"""
        while True:
            try:
                # Generate insights for all loaded datasets
                for dataset_id in self.datasets.keys():
                    self.generate_insights(dataset_id)
                
                # Sleep for a while before next generation
                time.sleep(300)  # Generate insights every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in background insight generation: {e}")
                time.sleep(60)
    
    def get_visualization(self, viz_id: str) -> Optional[Any]:
        """Get visualization by ID"""
        return self.visualizations.get(viz_id)
    
    def get_insights(self, dataset_id: str = None) -> List[InsightResult]:
        """Get insights for dataset"""
        if dataset_id:
            return [insight for insight in self.insights if dataset_id in str(insight.data_points)]
        return self.insights
    
    def export_visualization(self, viz_id: str, format: str = 'html', path: str = None) -> bool:
        """Export visualization to file"""
        viz = self.get_visualization(viz_id)
        if not viz:
            return False
        
        try:
            if format == 'html' and hasattr(viz, 'to_html'):
                if not path:
                    path = f"visualization_{viz_id}.html"
                viz.to_html(path)
                return True
            elif format == 'png' and hasattr(viz, 'write_image'):
                if not path:
                    path = f"visualization_{viz_id}.png"
                viz.write_image(path)
                return True
            else:
                self.logger.error(f"Unsupported export format: {format}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error exporting visualization: {e}")
            return False
    
    def create_dashboard(self, dataset_id: str) -> Optional[str]:
        """Create comprehensive dashboard for dataset"""
        if dataset_id not in self.datasets:
            return None
        
        df = self.datasets[dataset_id]
        dashboard_id = f"dashboard_{dataset_id}"
        
        try:
            if not PLOTLY_AVAILABLE:
                return None
            
            # Create subplots for dashboard
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Data Overview', 'Distribution', 'Trends', 'Correlations'),
                specs=[[{"type": "table"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "heatmap"}]]
            )
            
            # Add table with data overview
            fig.add_trace(
                go.Table(
                    header=dict(values=list(df.columns)),
                    cells=dict(values=[df[col] for col in df.columns])
                ),
                row=1, col=1
            )
            
            # Add distribution chart
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                fig.add_trace(
                    go.Histogram(x=df[numeric_cols[0]]),
                    row=1, col=2
                )
            
            # Add scatter plot
            if len(numeric_cols) >= 2:
                fig.add_trace(
                    go.Scatter(x=df[numeric_cols[0]], y=df[numeric_cols[1]], mode='markers'),
                    row=2, col=1
                )
            
            # Add correlation heatmap
            if len(numeric_cols) >= 2:
                corr_matrix = df[numeric_cols].corr()
                fig.add_trace(
                    go.Heatmap(z=corr_matrix.values, x=corr_matrix.columns, y=corr_matrix.index),
                    row=2, col=2
                )
            
            fig.update_layout(height=800, title_text=f"Dashboard for {dataset_id}")
            
            self.visualizations[dashboard_id] = fig
            return dashboard_id
            
        except Exception as e:
            self.logger.error(f"Error creating dashboard: {e}")
            return None 