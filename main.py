#!/usr/bin/env python3
"""
Flutter Earth - Dear PyGui Interface
Enhanced with features from the old HTML/CSS interface
"""

import dearpygui.dearpygui as dpg
import threading
import time
import json
import os
from pathlib import Path
from datetime import datetime
import logging
from bs4 import BeautifulSoup
import re
from tkinter import filedialog, Tk
import tkinter as tk

class FlutterEarthApp:
    """Enhanced Flutter Earth Application with Dear PyGui"""
    
    def __init__(self):
        # Initialize Dear PyGui
        dpg.create_context()
        
        # App state
        self.current_view = "dashboard"
        self.crawler_running = False
        self.download_running = False
        self.analysis_running = False
        self.html_analysis_running = False
        self.satellites = []
        self.datasets = []
        self.selected_satellite = None
        self.selected_dataset = None
        
        # HTML Analysis state
        self.html_file_path = ""
        self.parsed_data = []
        self.extracted_datasets = []
        self.analysis_progress = 0.0
        self.analysis_status = "Ready"
        
        # UI elements
        self.crawler_status_text = None
        self.crawler_progress_bar = None
        self.download_progress_bar = None
        self.download_status = None
        self.satellite_list = None
        self.dataset_list = None
        self.satellite_count_text = None
        self.dataset_count_text = None
        self.activity_log = None
        
        # HTML Analysis UI elements
        self.html_file_path_text = None
        self.html_analysis_status = None
        self.html_progress_bar = None
        self.html_results_list = None
        self.html_dataset_count = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize UI
        self.setup_themes()
        self.setup_fonts()
        self.create_main_window()
        
        # Load existing data if available
        self.load_existing_data()
    
    def setup_themes(self):
        """Setup modern themes inspired by the old interface"""
        with dpg.theme() as self.global_theme:
            with dpg.theme_component(dpg.mvAll):
                # Modern color scheme
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (45, 45, 45), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (74, 144, 226), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (57, 122, 189), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (45, 100, 160), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Header, (60, 60, 60), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (80, 80, 80), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (100, 100, 100), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (40, 40, 40), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (60, 60, 60), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, (74, 144, 226, 100), category=dpg.mvThemeCat_Core)
                
                # Modern styling
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 8, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 4, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 4, category=dpg.mvThemeCat_Core)
        
        # Light theme variant
        with dpg.theme() as self.light_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (248, 249, 250), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (33, 37, 41), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Header, (233, 236, 239), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (222, 226, 230), category=dpg.mvThemeCat_Core)
    
    def setup_fonts(self):
        """Setup modern fonts"""
        with dpg.font_registry():
            # Use Segoe UI if available, else Arial, else default
            try:
                self.default_font = dpg.add_font("C:/Windows/Fonts/segoeui.ttf", 18)
            except Exception:
                try:
                    self.default_font = dpg.add_font("C:/Windows/Fonts/arial.ttf", 18)
                except Exception:
                    self.default_font = None
        if self.default_font:
            dpg.bind_font(self.default_font)
    
    def create_main_window(self):
        """Create the main application window with modern toolbar"""
        dpg.create_viewport(title="Flutter Earth v2.0", width=1400, height=900)
        dpg.setup_dearpygui()
        
        # Create main window
        with dpg.window(label="Flutter Earth", tag="main_window", no_title_bar=True, no_resize=False, 
                       width=1400, height=900, pos=(0, 0)):
            
            # Top toolbar (inspired by the old interface)
            self.create_top_toolbar()
            
            # Main content area
            with dpg.child_window(width=1400, height=850, pos=(0, 50)):
                with dpg.tab_bar(tag="main_tab_bar"):
                    self.create_dashboard_tab()
                    self.create_satellites_tab()
                    self.create_html_analysis_tab()
        
        # Apply global theme
        dpg.bind_theme(self.global_theme)
    
    def create_top_toolbar(self):
        """Create modern top toolbar inspired by the old interface"""
        with dpg.group(horizontal=True, width=1400, height=50):
            # Left side - Navigation
            with dpg.group(horizontal=True):
                # App logo and title
                dpg.add_text("🛰️ Flutter Earth", color=(100, 200, 100))
                dpg.add_text("v2.0 - Ready", color=(150, 150, 150))
                
                dpg.add_separator()
                
                # Status indicators
                with dpg.group(horizontal=True):
                    dpg.add_text("Mode:")
                    dpg.add_text("Offline", color=(100, 255, 100))
                
                dpg.add_separator()
                
                # Quick status
                with dpg.group(horizontal=True):
                    dpg.add_text("Status:")
                    self.status_text = dpg.add_text("Ready", color=(100, 255, 100))
            
            # Right side - Actions
            with dpg.group(horizontal=True, pos=(1200, 0)):
                dpg.add_button(label="⚙️", callback=self.show_settings, width=30)
                dpg.add_button(label="?", callback=self.show_help, width=30)
                dpg.add_button(label="ℹ️", callback=self.show_about, width=30)
    
    def create_dashboard_tab(self):
        """Create enhanced dashboard tab"""
        with dpg.tab(label="🏠 Dashboard"):
            with dpg.group(horizontal=True):
                
                # Left panel - Status and controls
                with dpg.child_window(width=400, height=800):
                    dpg.add_text("System Status", color=(100, 200, 100))
                    dpg.add_separator()
                    
                    # Mode status
                    with dpg.group(horizontal=True):
                        dpg.add_text("Mode:")
                        dpg.add_text("Offline", color=(100, 255, 100))
                    
                    # Crawler status
                    with dpg.group(horizontal=True):
                        dpg.add_text("Earth Engine Crawler:")
                        self.crawler_status_text = dpg.add_text("Stopped", color=(255, 100, 100))
                    
                    # Crawler progress bar
                    self.crawler_progress_bar = dpg.add_progress_bar(default_value=0.0, width=350)
                    
                    dpg.add_separator()
                    
                    # Quick actions
                    dpg.add_text("Quick Actions", color=(100, 200, 100))
                    dpg.add_button(label="Start Earth Engine Crawler", callback=self.start_crawler, width=150)
                    dpg.add_button(label="Load Sample Data", callback=self.load_sample_data, width=150)
                    dpg.add_button(label="Generate Demo Data", callback=self.generate_demo_data, width=150)
                    
                    dpg.add_separator()
                    
                    # Statistics
                    dpg.add_text("Statistics", color=(100, 200, 100))
                    with dpg.group(horizontal=True):
                        dpg.add_text("Satellites:")
                        self.satellite_count_text = dpg.add_text("0")
                    
                    with dpg.group(horizontal=True):
                        dpg.add_text("Datasets:")
                        self.dataset_count_text = dpg.add_text("0")
                
                # Right panel - Charts and visualizations
                with dpg.child_window(width=950, height=800):
                    dpg.add_text("Data Overview", color=(100, 200, 100))
                    dpg.add_separator()
                    
                    # Placeholder for charts
                    with dpg.plot(label="Satellite Data Overview", height=300, width=900):
                        dpg.add_plot_legend()
                        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Time")
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Count")
                        
                        # Sample data for demonstration
                        x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                        y_data = [10, 15, 12, 18, 20, 25, 22, 28, 30, 35]
                        
                        dpg.add_line_series(x_data, y_data, label="Datasets", parent=y_axis)
                    
                    dpg.add_separator()
                    
                    # Recent activity
                    dpg.add_text("Recent Activity", color=(100, 200, 100))
                    self.activity_log = dpg.add_text("No recent activity")
    
    def create_satellites_tab(self):
        """Create enhanced satellites tab"""
        with dpg.tab(label="🛰️ Satellites"):
            with dpg.group(horizontal=True):
                
                # Left panel - Satellite list
                with dpg.child_window(width=400, height=750):
                    dpg.add_text("Available Satellites", color=(100, 200, 100))
                    dpg.add_separator()
                    
                    # Search box
                    dpg.add_input_text(label="Search Satellites", callback=self.filter_satellites)
                    
                    # Satellite list
                    with dpg.child_window(height=650):
                        self.satellite_list = dpg.add_listbox(
                            items=[],
                            callback=self.on_satellite_selected,
                            width=350
                        )
                
                # Right panel - Satellite details
                with dpg.child_window(width=950, height=750):
                    dpg.add_text("Satellite Details", color=(100, 200, 100))
                    dpg.add_separator()
                    
                    # Details area
                    with dpg.child_window(height=700):
                        self.satellite_details = dpg.add_text("Select a satellite to view details")
    
    # Remove or comment out all other tab creation methods (datasets, download, analysis, html_analysis, settings)
    
    def create_settings_tab(self):
        """Create enhanced settings tab with theme selection"""
        with dpg.tab(label="⚙️ Settings"):
            with dpg.child_window(height=800):
                dpg.add_text("Settings", color=(100, 200, 100))
                dpg.add_separator()
                
                # Theme Selection
                dpg.add_text("Appearance", color=(100, 200, 100))
                dpg.add_combo(
                    label="Theme",
                    items=["Dark", "Light", "Custom"],
                    default_value="Dark",
                    callback=self.set_theme
                )
                
                # Theme Options
                dpg.add_text("Theme Options", color=(100, 200, 100))
                dpg.add_checkbox(label="Enable Animated Backgrounds", tag="animated_bg")
                dpg.add_combo(
                    label="Toolbar Animation",
                    items=["Glow", "Bounce", "Slide", "Pulse", "None"],
                    default_value="Glow",
                    tag="toolbar_animation"
                )
                
                # General Settings
                dpg.add_text("General", color=(100, 200, 100))
                with dpg.group(horizontal=True):
                    dpg.add_input_text(label="Default Output Directory", tag="settings_output_dir", width=400)
                    dpg.add_button(label="Browse", callback=self.browse_settings_output)
                
                # Actions
                dpg.add_text("Actions", color=(100, 200, 100))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Reload Settings", callback=self.reload_settings)
                    dpg.add_button(label="Clear Cache", callback=self.clear_cache)
                    dpg.add_button(label="Authenticate", callback=self.authenticate)
    
    # Callback methods
    def start_crawler(self):
        """Start the Earth Engine catalog crawler"""
        if not self.crawler_running:
            self.crawler_running = True
            dpg.set_value(self.crawler_status_text, "Running...")
            dpg.configure_item(self.crawler_status_text, color=(100, 255, 100))
            
            # Start real crawler in background thread
            thread = threading.Thread(target=self._run_real_crawler)
            thread.daemon = True
            thread.start()
            
            self.log_activity("Started Earth Engine catalog crawler")
    
    def _run_real_crawler(self):
        """Run real Earth Engine catalog crawler"""
        try:
            # Import the advanced crawler
            from advanced_earth_engine_crawler import AdvancedEarthEngineCrawler
            
            # Create crawler instance
            crawler = AdvancedEarthEngineCrawler()
            
            # Update progress
            dpg.set_value(self.crawler_progress_bar, 10)
            
            # Run the crawler
            results = crawler.crawl_all_datasets()
            
            # Update progress
            dpg.set_value(self.crawler_progress_bar, 90)
            
            # Load the results into the application
            if results and 'datasets' in results:
                self.satellites = []
                self.datasets = results['datasets']
                
                # Convert datasets to satellite format for display
                for dataset in self.datasets:
                    satellite_info = {
                        "name": dataset.get('satellite', 'Unknown'),
                        "description": dataset.get('description', ''),
                        "resolution": dataset.get('resolution', 'Variable'),
                        "bands": dataset.get('bands', []),
                        "applications": dataset.get('applications', []),
                        "status": "Active"
                    }
                    self.satellites.append(satellite_info)
                
                # Update UI in main thread
                dpg.set_value(self.crawler_progress_bar, 100)
                self._crawler_finished()
            else:
                self._crawler_error("No data found")
                
        except Exception as e:
            self._crawler_error(str(e))
    
    def _run_demo_crawler(self):
        """Run demo crawler simulation"""
        try:
            # Simulate crawling progress
            for i in range(101):
                if not self.crawler_running:
                    break
                time.sleep(0.1)
                # Update progress directly
                dpg.set_value(self.crawler_progress_bar, i)
            
            if self.crawler_running:
                self._crawler_finished()
                
        except Exception as e:
            self._crawler_error(str(e))
    
    def _crawler_finished(self):
        """Handle crawler completion"""
        self.crawler_running = False
        dpg.set_value(self.crawler_status_text, "Completed")
        dpg.configure_item(self.crawler_status_text, color=(100, 255, 100))
        self.generate_demo_data()
        self.log_activity("Earth Engine catalog crawler completed successfully")
    
    def _crawler_error(self, error):
        """Handle crawler error"""
        self.crawler_running = False
        dpg.set_value(self.crawler_status_text, f"Error: {error}")
        dpg.configure_item(self.crawler_status_text, color=(255, 100, 100))
        self.log_activity(f"Earth Engine crawler error: {error}")
    
    def stop_crawler(self):
        """Stop the Earth Engine crawler"""
        self.crawler_running = False
        dpg.set_value(self.crawler_status_text, "Stopped")
        dpg.configure_item(self.crawler_status_text, color=(255, 100, 100))
        self.log_activity("Earth Engine catalog crawler stopped")
    
    def generate_demo_data(self):
        """Generate demo satellite and dataset data"""
        self.satellites = self.get_demo_satellites()
        self.datasets = self.get_demo_datasets()
        
        # Update UI
        satellite_names = [sat["name"] for sat in self.satellites]
        dataset_names = [ds["name"] for ds in self.datasets]
        
        dpg.configure_item(self.satellite_list, items=satellite_names)
        dpg.configure_item(self.dataset_list, items=dataset_names)
        
        dpg.set_value(self.satellite_count_text, str(len(self.satellites)))
        dpg.set_value(self.dataset_count_text, str(len(self.datasets)))
        
        self.log_activity(f"Generated {len(self.satellites)} demo satellites and {len(self.datasets)} datasets")
    
    def load_sample_data(self):
        """Load sample satellite and dataset data"""
        self.satellites = self.get_sample_satellites()
        self.datasets = self.get_sample_datasets()
        
        # Update UI
        satellite_names = [sat["name"] for sat in self.satellites]
        dataset_names = [ds["name"] for ds in self.datasets]
        
        dpg.configure_item(self.satellite_list, items=satellite_names)
        dpg.configure_item(self.dataset_list, items=dataset_names)
        
        dpg.set_value(self.satellite_count_text, str(len(self.satellites)))
        dpg.set_value(self.dataset_count_text, str(len(self.datasets)))
        
        self.log_activity(f"Loaded {len(self.satellites)} satellites and {len(self.datasets)} datasets")
    
    def get_sample_satellites(self):
        """Get sample satellite data"""
        return [
            {
                "name": "Landsat 8",
                "description": "Landsat 8 Operational Land Imager and Thermal Infrared Sensor",
                "resolution": "15-100m",
                "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11"],
                "applications": ["Agriculture", "Forestry", "Urban Planning", "Water Resources"],
                "status": "Active"
            },
            {
                "name": "Sentinel-2",
                "description": "Sentinel-2 MultiSpectral Instrument",
                "resolution": "10-60m",
                "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"],
                "applications": ["Agriculture", "Forestry", "Land Cover", "Disaster Management"],
                "status": "Active"
            },
            {
                "name": "MODIS",
                "description": "Moderate Resolution Imaging Spectroradiometer",
                "resolution": "250m-1km",
                "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7"],
                "applications": ["Climate Studies", "Vegetation Monitoring", "Ocean Studies"],
                "status": "Active"
            }
        ]
    
    def get_demo_satellites(self):
        """Get demo satellite data with more variety"""
        return [
            {
                "name": "Landsat 8",
                "description": "Landsat 8 Operational Land Imager and Thermal Infrared Sensor",
                "resolution": "15-100m",
                "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11"],
                "applications": ["Agriculture", "Forestry", "Urban Planning", "Water Resources"],
                "status": "Active"
            },
            {
                "name": "Sentinel-2",
                "description": "Sentinel-2 MultiSpectral Instrument",
                "resolution": "10-60m",
                "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"],
                "applications": ["Agriculture", "Forestry", "Land Cover", "Disaster Management"],
                "status": "Active"
            },
            {
                "name": "MODIS",
                "description": "Moderate Resolution Imaging Spectroradiometer",
                "resolution": "250m-1km",
                "bands": ["B1", "B2", "B3", "B4", "B5", "B6", "B7"],
                "applications": ["Climate Studies", "Vegetation Monitoring", "Ocean Studies"],
                "status": "Active"
            },
            {
                "name": "Sentinel-1",
                "description": "Sentinel-1 Radar Imaging Mission",
                "resolution": "5-40m",
                "bands": ["C-Band SAR"],
                "applications": ["Disaster Management", "Marine Monitoring", "Land Deformation"],
                "status": "Active"
            },
            {
                "name": "GOES-16",
                "description": "Geostationary Operational Environmental Satellite",
                "resolution": "0.5-2km",
                "bands": ["Visible", "Infrared", "Water Vapor"],
                "applications": ["Weather Monitoring", "Climate Studies", "Atmospheric Research"],
                "status": "Active"
            }
        ]
    
    def get_sample_datasets(self):
        """Get sample dataset data"""
        return [
            {
                "name": "Landsat 8 Surface Reflectance",
                "description": "Atmospherically corrected surface reflectance data",
                "satellite": "Landsat 8",
                "resolution": "30m",
                "temporal_coverage": "2013-present"
            },
            {
                "name": "Sentinel-2 Level-2A",
                "description": "Atmospherically corrected surface reflectance data",
                "satellite": "Sentinel-2",
                "resolution": "10m",
                "temporal_coverage": "2017-present"
            },
            {
                "name": "MODIS Terra Surface Reflectance",
                "description": "8-day surface reflectance composite",
                "satellite": "MODIS",
                "resolution": "500m",
                "temporal_coverage": "2000-present"
            }
        ]
    
    def get_demo_datasets(self):
        """Get demo dataset data with more variety"""
        return [
            {
                "name": "Landsat 8 Surface Reflectance",
                "description": "Atmospherically corrected surface reflectance data",
                "satellite": "Landsat 8",
                "resolution": "30m",
                "temporal_coverage": "2013-present"
            },
            {
                "name": "Sentinel-2 Level-2A",
                "description": "Atmospherically corrected surface reflectance data",
                "satellite": "Sentinel-2",
                "resolution": "10m",
                "temporal_coverage": "2017-present"
            },
            {
                "name": "MODIS Terra Surface Reflectance",
                "description": "8-day surface reflectance composite",
                "satellite": "MODIS",
                "resolution": "500m",
                "temporal_coverage": "2000-present"
            },
            {
                "name": "Sentinel-1 GRD",
                "description": "Ground Range Detected radar data",
                "satellite": "Sentinel-1",
                "resolution": "10m",
                "temporal_coverage": "2014-present"
            },
            {
                "name": "GOES-16 ABI",
                "description": "Advanced Baseline Imager data",
                "satellite": "GOES-16",
                "resolution": "0.5km",
                "temporal_coverage": "2017-present"
            }
        ]
    
    def on_satellite_selected(self, sender, app_data):
        """Handle satellite selection"""
        try:
            # Find the satellite by name (remove status icon if present)
            selected_name = app_data
            if selected_name.startswith(('✅', '⏳', '❌')):
                selected_name = selected_name[2:].strip()  # Remove status icon and space
            
            # Find the satellite in our list
            for satellite in self.satellites:
                if satellite.get('name', '') == selected_name:
                    self.selected_satellite = satellite
                    
                    details = f"""
Name: {satellite.get('name', 'Unknown')}
Description: {satellite.get('description', 'No description available')}
Status: {satellite.get('status', 'Unknown')}
URL: {satellite.get('url', 'No URL available')}

Provider: {satellite.get('provider', 'Unknown')}
Resolution: {satellite.get('resolution', 'Unknown')}
Launch Date: {satellite.get('launch_date', 'Unknown')}
Coverage: {satellite.get('coverage', 'Unknown')}
Frequency: {satellite.get('frequency', 'Unknown')}

Bands: {', '.join(satellite.get('bands', [])) if satellite.get('bands') else 'No band information'}

Dataset Links: {len(satellite.get('dataset_links', []))} available
Images: {len(satellite.get('images', []))} available

Extracted: {satellite.get('extracted_at', 'Unknown')}
"""
                    dpg.set_value(self.satellite_details, details)
                    break
            else:
                dpg.set_value(self.satellite_details, "Satellite not found in data")
                
        except Exception as e:
            self.log_activity(f"Error selecting satellite: {e}")
            dpg.set_value(self.satellite_details, f"Error: {str(e)}")
    
    def on_dataset_selected(self, sender, app_data):
        """Handle dataset selection"""
        if app_data < len(self.datasets):
            self.selected_dataset = self.datasets[app_data]
            dataset = self.selected_dataset
            
            details = f"""
Name: {dataset['name']}
Description: {dataset['description']}
Satellite: {dataset.get('satellite', 'Unknown')}
Resolution: {dataset.get('resolution', 'Variable')}
Temporal Coverage: {dataset.get('temporal_coverage', 'Unknown')}
"""
            dpg.set_value(self.dataset_details, details)
    
    def filter_satellites(self, sender, app_data):
        """Filter satellites based on search term"""
        if app_data:
            filtered = [sat for sat in self.satellites if app_data.lower() in sat['name'].lower()]
            satellite_names = [sat["name"] for sat in filtered]
            dpg.configure_item(self.satellite_list, items=satellite_names)
        else:
            satellite_names = [sat["name"] for sat in self.satellites]
            dpg.configure_item(self.satellite_list, items=satellite_names)
    
    def filter_datasets(self, sender, app_data):
        """Filter datasets based on search term"""
        if app_data:
            filtered = [ds for ds in self.datasets if app_data.lower() in ds['name'].lower()]
            dataset_names = [ds["name"] for ds in filtered]
            dpg.configure_item(self.dataset_list, items=dataset_names)
        else:
            dataset_names = [ds["name"] for ds in self.datasets]
            dpg.configure_item(self.dataset_list, items=dataset_names)
    
    def start_download(self):
        """Start download process"""
        if not self.download_running:
            self.download_running = True
            dpg.set_value(self.download_status, "Starting download...")
            
            # Start demo download in background thread
            thread = threading.Thread(target=self._run_demo_download)
            thread.daemon = True
            thread.start()
            
            self.log_activity("Started demo download")
    
    def _run_demo_download(self):
        """Run demo download simulation"""
        try:
            # Simulate download progress
            for i in range(101):
                if not self.download_running:
                    break
                time.sleep(0.1)
                dpg.set_value(self.download_progress_bar, i)
                
                # Update log
                if i % 10 == 0:
                    log_message = f"Download progress: {i}% - Processing data..."
                    dpg.set_value(self.download_log, log_message)
            
            if self.download_running:
                self._download_finished()
                
        except Exception as e:
            self._download_error(str(e))
    
    def _download_finished(self):
        """Handle download completion"""
        self.download_running = False
        dpg.set_value(self.download_status, "Download completed successfully")
        dpg.set_value(self.download_log, "Download completed successfully!")
        self.log_activity("Demo download completed")
    
    def _download_error(self, error):
        """Handle download error"""
        self.download_running = False
        dpg.set_value(self.download_status, f"Download error: {error}")
        dpg.set_value(self.download_log, f"Download failed: {error}")
        self.log_activity(f"Download error: {error}")
    
    def cancel_download(self):
        """Cancel download"""
        self.download_running = False
        dpg.set_value(self.download_status, "Download cancelled")
        self.log_activity("Download cancelled")
    
    def fill_sample_data(self):
        """Fill download form with sample data"""
        dpg.set_value("aoi_input", "[minLon, minLat, maxLon, maxLat]")
        dpg.set_value("start_date", "2023-01-01")
        dpg.set_value("end_date", "2023-12-31")
        dpg.set_value("sensor_select", "Landsat 8")
        dpg.set_value("output_dir", "./downloads")
        self.log_activity("Filled sample data")
    
    def run_analysis(self):
        """Run analysis process"""
        if not self.analysis_running:
            self.analysis_running = True
            dpg.set_value(self.analysis_results, "Running analysis...")
            
            # Start demo analysis in background thread
            thread = threading.Thread(target=self._run_demo_analysis)
            thread.daemon = True
            thread.start()
            
            self.log_activity("Started demo analysis")
    
    def _run_demo_analysis(self):
        """Run demo analysis simulation"""
        try:
            # Simulate analysis progress
            for i in range(101):
                if not self.analysis_running:
                    break
                time.sleep(0.05)
                
                if i == 50:
                    dpg.set_value(self.analysis_results, "Processing data...")
                elif i == 80:
                    dpg.set_value(self.analysis_results, "Generating results...")
                elif i == 100:
                    dpg.set_value(self.analysis_results, "Analysis completed successfully!")
            
            if self.analysis_running:
                self._analysis_finished()
                
        except Exception as e:
            self._analysis_error(str(e))
    
    def _analysis_finished(self):
        """Handle analysis completion"""
        self.analysis_running = False
        self.log_activity("Demo analysis completed")
    
    def _analysis_error(self, error):
        """Handle analysis error"""
        self.analysis_running = False
        dpg.set_value(self.analysis_results, f"Analysis error: {error}")
        self.log_activity(f"Analysis error: {error}")
    
    def set_theme(self, sender, app_data):
        """Set application theme"""
        if app_data == "Dark":
            dpg.bind_theme(self.global_theme)
        elif app_data == "Light":
            dpg.bind_theme(self.light_theme)
        self.log_activity(f"Changed theme to {app_data}")
    
    def browse_html_file(self):
        """Browse for HTML file to analyze"""
        try:
            # Create a hidden Tkinter root window
            root = Tk()
            root.withdraw()  # Hide the root window
            
            # Open file dialog
            file_path = filedialog.askopenfilename(
                title="Select HTML File",
                filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
            )
            
            if file_path:
                self.html_file_path = file_path
                dpg.set_value("html_file_path", file_path)
                dpg.set_value(self.html_analysis_status, f"Selected file: {os.path.basename(file_path)}")
                self.log_activity(f"Selected HTML file: {os.path.basename(file_path)}")
            
            root.destroy()
            
        except Exception as e:
            self.log_activity(f"Error browsing for HTML file: {e}")
    
    def run_html_analysis(self):
        """Run HTML analysis process"""
        if not self.html_file_path:
            dpg.set_value(self.html_analysis_status, "Please select an HTML file first")
            return
        
        if not self.html_analysis_running:
            self.html_analysis_running = True
            dpg.set_value(self.html_analysis_status, "Starting HTML analysis...")
            dpg.set_value(self.html_progress_bar, 0.0)
            
            # Start analysis in background thread
            thread = threading.Thread(target=self._run_html_analysis)
            thread.daemon = True
            thread.start()
            
            self.log_activity("Started HTML analysis")
    
    def _extract_datasets_from_html(self, soup):
        """Extract satellite links and information from HTML"""
        satellites = []
        
        # Look for satellite thumbnail links - common patterns in Earth Engine catalog
        satellite_links = []
        
        # Method 1: Look for links with satellite-related hrefs
        satellite_links.extend(soup.find_all('a', href=re.compile(r'satellite|mission|platform', re.I)))
        
        # Method 2: Look for links with image thumbnails that might be satellites
        img_links = soup.find_all('a', href=True)
        for link in img_links:
            img = link.find('img')
            if img and (img.get('alt', '').lower().find('satellite') != -1 or 
                       img.get('src', '').lower().find('satellite') != -1):
                satellite_links.append(link)
        
        # Method 3: Look for links with satellite names in text
        satellite_name_patterns = [
            r'Landsat', r'Sentinel', r'MODIS', r'GOES', r'NOAA', r'SPOT', 
            r'RapidEye', r'Planet', r'WorldView', r'IKONOS', r'QuickBird',
            r'ALOS', r'Envisat', r'ERS', r'Radarsat', r'TerraSAR-X'
        ]
        
        for pattern in satellite_name_patterns:
            pattern_links = soup.find_all('a', string=re.compile(pattern, re.I))
            satellite_links.extend(pattern_links)
        
        # Method 4: Look for div containers with satellite info
        satellite_containers = soup.find_all(['div', 'article', 'section'], 
                                           class_=re.compile(r'satellite|mission|platform|card', re.I))
        
        # Extract satellite information from links
        for link in satellite_links:
            satellite_info = self._extract_satellite_from_link(link)
            if satellite_info:
                satellites.append(satellite_info)
        
        # Extract from containers
        for container in satellite_containers:
            satellite_info = self._extract_satellite_from_container(container)
            if satellite_info:
                satellites.append(satellite_info)
        
        # Remove duplicates based on name
        unique_satellites = []
        seen_names = set()
        for satellite in satellites:
            name = satellite.get('name', '')
            if name and name not in seen_names:
                unique_satellites.append(satellite)
                seen_names.add(name)
        
        return unique_satellites
    
    def _extract_satellite_from_link(self, link):
        """Extract satellite information from a link element"""
        try:
            name = link.get_text(strip=True)
            href = link.get('href', '')
            
            # Get image if available
            img = link.find('img')
            thumbnail = img.get('src', '') if img else ''
            alt_text = img.get('alt', '') if img else ''
            
            # Determine if this is a satellite link
            if (name and len(name) > 2 and 
                (href or any(pattern in name for pattern in ['Landsat', 'Sentinel', 'MODIS', 'GOES', 'NOAA']))):
                
                return {
                    'name': name,
                    'url': href,
                    'thumbnail': thumbnail,
                    'alt_text': alt_text,
                    'source': 'link_extraction',
                    'extracted_at': datetime.now().isoformat(),
                    'status': 'pending_crawl'  # Mark for crawling
                }
        except Exception as e:
            self.logger.error(f"Error extracting from link: {e}")
        
        return None
    
    def _extract_satellite_from_container(self, container):
        """Extract satellite information from a container element"""
        try:
            # Look for satellite name
            name_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b'])
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            # Look for description
            desc_elem = container.find(['p', 'div', 'span'], class_=re.compile(r'desc|summary|abstract', re.I))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Look for image
            img = container.find('img')
            thumbnail = img.get('src', '') if img else ''
            
            # Look for link
            link = container.find('a')
            url = link.get('href', '') if link else ''
            
            if name and len(name) > 2:
                return {
                    'name': name,
                    'description': description,
                    'url': url,
                    'thumbnail': thumbnail,
                    'source': 'container_extraction',
                    'extracted_at': datetime.now().isoformat(),
                    'status': 'pending_crawl'
                }
        except Exception as e:
            self.logger.error(f"Error extracting from container: {e}")
        
        return None
    
    def _run_html_analysis(self):
        """Run HTML analysis and satellite crawling in background thread"""
        try:
            # Update status
            dpg.set_value(self.html_analysis_status, "Loading HTML file...")
            dpg.set_value(self.html_progress_bar, 0.05)
            
            # Read HTML file
            with open(self.html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            dpg.set_value(self.html_analysis_status, "Parsing HTML content...")
            dpg.set_value(self.html_progress_bar, 0.1)
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            dpg.set_value(self.html_analysis_status, "Extracting satellite links...")
            dpg.set_value(self.html_progress_bar, 0.2)
            
            # Extract satellite links
            satellites = self._extract_datasets_from_html(soup)
            
            dpg.set_value(self.html_analysis_status, f"Found {len(satellites)} satellites. Starting detailed crawling...")
            dpg.set_value(self.html_progress_bar, 0.3)
            
            # Crawl each satellite for detailed information
            detailed_satellites = []
            for i, satellite in enumerate(satellites):
                if not self.html_analysis_running:
                    break
                
                # Update progress
                progress = 0.3 + (0.6 * i / len(satellites))
                dpg.set_value(self.html_progress_bar, progress)
                dpg.set_value(self.html_analysis_status, f"Crawling satellite {i+1}/{len(satellites)}: {satellite.get('name', 'Unknown')}")
                
                # Crawl satellite details
                detailed_info = self._crawl_satellite_details(satellite)
                if detailed_info:
                    detailed_satellites.append(detailed_info)
                
                # Update UI in real-time
                self._update_satellite_list(detailed_satellites)
                
                # Small delay to prevent overwhelming the server
                time.sleep(0.5)
            
            dpg.set_value(self.html_analysis_status, "Processing final data...")
            dpg.set_value(self.html_progress_bar, 0.9)
            
            # Store extracted data
            self.extracted_datasets = detailed_satellites
            self.parsed_data = self._process_extracted_data(detailed_satellites)
            
            dpg.set_value(self.html_analysis_status, "Saving to JSON...")
            dpg.set_value(self.html_progress_bar, 0.95)
            
            # Save to JSON file
            self._save_extracted_data()
            
            dpg.set_value(self.html_analysis_status, f"Analysis completed! Found {len(detailed_satellites)} detailed satellites")
            dpg.set_value(self.html_progress_bar, 1.0)
            
            # Update UI with final results
            self._update_html_analysis_results()
            
            self.html_analysis_running = False
            self.log_activity(f"HTML analysis completed - Found {len(detailed_satellites)} detailed satellites")
            
        except Exception as e:
            self.html_analysis_running = False
            dpg.set_value(self.html_analysis_status, f"Analysis error: {str(e)}")
            self.log_activity(f"HTML analysis error: {str(e)}")
    
    def _crawl_satellite_details(self, satellite):
        """Crawl individual satellite page for detailed information"""
        try:
            url = satellite.get('url', '')
            if not url:
                return satellite
            
            # Make URL absolute if it's relative
            if url.startswith('/'):
                # Extract base URL from the HTML file path
                base_url = self._extract_base_url()
                url = base_url + url
            elif not url.startswith('http'):
                # Assume it's relative to the current directory
                base_url = self._extract_base_url()
                url = base_url + '/' + url
            
            # Use requests to fetch the satellite page
            import requests
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse the satellite page
            satellite_soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract detailed information
            detailed_info = satellite.copy()
            detailed_info.update(self._extract_satellite_page_details(satellite_soup))
            detailed_info['status'] = 'crawled'
            detailed_info['crawled_at'] = datetime.now().isoformat()
            
            return detailed_info
            
        except Exception as e:
            self.logger.error(f"Error crawling satellite {satellite.get('name', 'Unknown')}: {e}")
            # Return original satellite info with error status
            satellite['status'] = 'crawl_error'
            satellite['error'] = str(e)
            return satellite
    
    def _extract_satellite_page_details(self, soup):
        """Extract detailed information from a satellite page"""
        details = {}
        
        try:
            # Extract description
            desc_selectors = [
                'meta[name="description"]',
                '.description', '.summary', '.abstract',
                'p', 'div[class*="desc"]', 'div[class*="summary"]'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    description = desc_elem.get_text(strip=True) if hasattr(desc_elem, 'get_text') else desc_elem.get('content', '')
                    if description and len(description) > 20:
                        details['description'] = description
                        break
            
            # Extract specifications
            spec_patterns = {
                'launch_date': r'\b(19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b',
                'resolution': r'\b\d+(?:\.\d+)?\s*(?:m|meter|meters|km|kilometer|kilometers)\b',
                'coverage': r'\b(?:global|worldwide|regional|local)\b',
                'frequency': r'\b\d+(?:\.\d+)?\s*(?:day|days|hour|hours|minute|minutes)\b',
                'bands': r'\b(?:red|green|blue|nir|swir|thermal|panchromatic)\b',
                'provider': r'\b(?:NASA|ESA|USGS|NOAA|JAXA|CSA|ROSCOSMOS)\b'
            }
            
            page_text = soup.get_text()
            for key, pattern in spec_patterns.items():
                matches = re.findall(pattern, page_text, re.I)
                if matches:
                    details[key] = matches[0] if len(matches) == 1 else matches[:3]
            
            # Extract links to datasets
            dataset_links = soup.find_all('a', href=re.compile(r'dataset|catalog|collection', re.I))
            if dataset_links:
                details['dataset_links'] = [{'name': link.get_text(strip=True), 'url': link.get('href', '')} 
                                          for link in dataset_links[:10]]  # Limit to first 10
            
            # Extract images
            images = soup.find_all('img')
            if images:
                details['images'] = [img.get('src', '') for img in images if img.get('src', '')][:5]  # Limit to first 5
            
        except Exception as e:
            self.logger.error(f"Error extracting satellite page details: {e}")
        
        return details
    
    def _extract_base_url(self):
        """Extract base URL from the HTML file path"""
        # This is a simplified approach - in a real scenario, you'd want to parse the HTML
        # to find the actual base URL or domain
        return "https://developers.google.com/earth-engine/datasets"
    
    def _update_satellite_list(self, satellites):
        """Update the satellite list in real-time"""
        try:
            # Update the main satellite list
            self.satellites = satellites
            
            # Update satellite count
            dpg.set_value(self.satellite_count_text, str(len(satellites)))
            
            # Update satellite list in the satellites tab
            satellite_items = []
            for satellite in satellites:
                name = satellite.get('name', 'Unknown')
                status = satellite.get('status', 'unknown')
                status_icon = '✅' if status == 'crawled' else '⏳' if status == 'pending_crawl' else '❌'
                satellite_items.append(f"{status_icon} {name}")
            
            dpg.configure_item(self.satellite_list, items=satellite_items)
            
        except Exception as e:
            self.log_activity(f"Error updating satellite list: {e}")
    
    def _update_html_analysis_results(self):
        """Update UI with analysis results"""
        try:
            # Update dataset count
            dpg.set_value(self.html_dataset_count, str(len(self.extracted_datasets)))
            
            # Update results list with satellite information
            result_items = []
            for i, satellite in enumerate(self.extracted_datasets[:50]):  # Limit to first 50
                name = satellite.get('name', 'Unknown')
                status = satellite.get('status', 'unknown')
                status_icon = '✅' if status == 'crawled' else '⏳' if status == 'pending_crawl' else '❌'
                result_items.append(f"{i+1}. {status_icon} {name}")
            
            if len(self.extracted_datasets) > 50:
                result_items.append(f"... and {len(self.extracted_datasets) - 50} more satellites")
            
            dpg.configure_item(self.html_results_list, items=result_items)
            
        except Exception as e:
            self.log_activity(f"Error updating HTML analysis results: {e}")
    
    def _process_extracted_data(self, satellites):
        """Process and organize extracted satellite data"""
        processed_data = {
            'total_satellites': len(satellites),
            'extraction_timestamp': datetime.now().isoformat(),
            'source_file': self.html_file_path,
            'satellites': satellites,
            'summary': {
                'by_status': {},
                'by_provider': {},
                'by_resolution': {}
            }
        }
        
        # Generate summary statistics
        for satellite in satellites:
            status = satellite.get('status', 'unknown')
            processed_data['summary']['by_status'][status] = processed_data['summary']['by_status'].get(status, 0) + 1
            
            provider = satellite.get('provider', 'unknown')
            if provider and provider != 'unknown':
                processed_data['summary']['by_provider'][provider] = processed_data['summary']['by_provider'].get(provider, 0) + 1
        
        return processed_data
    
    def _save_extracted_data(self):
        """Save extracted data to JSON file"""
        try:
            # Create output directory if it doesn't exist
            output_dir = Path("extracted_data")
            output_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"satellite_analysis_{timestamp}.json"
            filepath = output_dir / filename
            
            # Save data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.parsed_data, f, indent=2, ensure_ascii=False)
            
            self.log_activity(f"Saved extracted satellite data to {filepath}")
            
        except Exception as e:
            self.log_activity(f"Error saving extracted data: {e}")
    
    def create_html_analysis_tab(self):
        """Create enhanced HTML Analysis tab for satellite extraction"""
        with dpg.tab(label="📄 HTML Analysis"):
            with dpg.child_window(height=800):
                dpg.add_text("Satellite Data Extraction", color=(100, 200, 100))
                dpg.add_separator()
                
                # File selection
                with dpg.group(horizontal=True):
                    dpg.add_text("HTML File *", color=(100, 200, 100))
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(label="File Path", tag="html_file_path", width=400, default_value=self.html_file_path)
                        dpg.add_button(label="Browse", callback=self.browse_html_file)
                
                # Analysis Options
                with dpg.group():
                    dpg.add_text("Extraction Options")
                    
                    # Analysis Type
                    dpg.add_combo(
                        label="Extraction Type",
                        items=["Extract Satellites", "Extract Missions", "Extract Platforms", "Extract All"],
                        default_value="Extract Satellites",
                        tag="html_analysis_type"
                    )
                    
                    # Parameters (JSON)
                    dpg.add_input_text(label="Parameters (JSON)", tag="html_analysis_params", width=400)
                    
                    dpg.add_separator()
                    
                    # Run Analysis Button
                    dpg.add_button(label="Extract Satellite Data", callback=self.run_html_analysis, width=200)
                    
                    # Status and Progress
                    self.html_analysis_status = dpg.add_text("Ready for satellite extraction")
                    self.html_progress_bar = dpg.add_progress_bar(default_value=0.0, width=400)
                    
                    # Results List
                    self.html_results_list = dpg.add_listbox(
                        items=[],
                        width=400
                    )
                    dpg.add_text("Extracted Satellites:", parent=self.html_results_list)
                    dpg.add_separator()
                    dpg.add_text("Satellite Count:", parent=self.html_results_list)
                    self.html_dataset_count = dpg.add_text("0")
    
    def load_existing_data(self):
        """Load existing extracted data if available"""
        try:
            output_dir = Path("extracted_data")
            if output_dir.exists():
                json_files = list(output_dir.glob("*.json"))
                if json_files:
                    # Load the most recent file
                    latest_file = max(json_files, key=lambda x: x.stat().st_mtime)
                    with open(latest_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    self.parsed_data = data
                    self.extracted_datasets = data.get('datasets', [])
                    
                    # Update UI
                    dpg.set_value(self.html_dataset_count, str(len(self.extracted_datasets)))
                    self.log_activity(f"Loaded existing data from {latest_file.name}")
                    
        except Exception as e:
            self.log_activity(f"Error loading existing data: {e}")
    
    def browse_output_dir(self):
        """Browse for output directory"""
        # This would open a file dialog in a real implementation
        dpg.set_value("output_dir", "./downloads")
        self.log_activity("Selected output directory")
    
    def browse_analysis_file(self):
        """Browse for analysis file"""
        # This would open a file dialog in a real implementation
        dpg.set_value("analysis_file", "./data/sample.tif")
        self.log_activity("Selected analysis file")
    
    def browse_settings_output(self):
        """Browse for settings output directory"""
        # This would open a file dialog in a real implementation
        dpg.set_value("settings_output_dir", "./output")
        self.log_activity("Selected settings output directory")
    
    def open_map_selector(self):
        """Open map selector"""
        self.log_activity("Opened map selector")
    
    def show_calendar(self, target):
        """Show calendar for date selection"""
        self.log_activity(f"Opened calendar for {target}")
    
    def show_settings(self):
        """Show settings"""
        dpg.set_value("main_tab_bar", 5)  # Switch to settings tab
        self.log_activity("Opened settings")
    
    def show_help(self):
        """Show help"""
        self.log_activity("Opened help")
    
    def show_about(self):
        """Show about dialog"""
        self.log_activity("Opened about dialog")
    
    def reload_settings(self):
        """Reload settings"""
        self.log_activity("Reloaded settings")
    
    def clear_cache(self):
        """Clear cache"""
        self.log_activity("Cleared cache")
    
    def authenticate(self):
        """Authenticate with Earth Engine"""
        self.log_activity("Authentication requested")
    
    def save_settings(self):
        """Save settings"""
        self.log_activity("Settings saved")
    
    def log_activity(self, message):
        """Log activity message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        dpg.set_value(self.activity_log, log_entry)
    
    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists("settings.json"):
                with open("settings.json", "r") as f:
                    settings = json.load(f)
                    # Apply settings
                    return settings
        except Exception as e:
            self.logger.error(f"Error loading settings: {e}")
        return {}
    
    def run(self):
        """Run the application"""
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

def main():
    """Main function"""
    app = FlutterEarthApp()
    app.run()

if __name__ == "__main__":
    main() 