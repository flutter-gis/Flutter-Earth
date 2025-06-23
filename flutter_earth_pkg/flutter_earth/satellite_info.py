"""Satellite information and details for Flutter Earth."""
from typing import Dict, Any, List, Tuple
from datetime import datetime
from .config import SATELLITE_DETAILS

# Satellite timeline information
SENSOR_TIMELINE = {
    'LANDSAT_9': ('2021-09-27', None),
    'LANDSAT_8': ('2013-04-11', None),
    'LANDSAT_7': ('1999-04-15', '2022-04-06'),
    'LANDSAT_5': ('1984-03-01', '2013-06-05'),
    'LANDSAT_4': ('1982-07-16', '1993-12-14'),
    'SENTINEL2': ('2015-06-23', None),
    'VIIRS': ('2012-01-18', None),
    'MODIS': ('2000-02-24', None),
    'ERA5_TEMP': ('1950-01-01', None),
}

# Data collections for each sensor
DATA_COLLECTIONS = {
    'LANDSAT_9': ["LANDSAT/LC09/C02/T1_L2"],
    'LANDSAT_8': ["LANDSAT/LC08/C02/T1_L2"],
    'LANDSAT_7': ["LANDSAT/LE07/C02/T1_L2"],
    'LANDSAT_5': ["LANDSAT/LT05/C02/T1_L2"],
    'LANDSAT_4': ["LANDSAT/LT04/C02/T1_L2"],
    'SENTINEL2': ["COPERNICUS/S2_SR_HARMONIZED"],
    'VIIRS': ["NOAA/VIIRS/001/VNP09GA"],
    'MODIS': ["MODIS/061/MOD09GA"],
    'ERA5_TEMP': ["ECMWF/ERA5_LAND/DAILY_AGGR"],
}

# Detailed satellite information
SATELLITE_DETAILS = {
    'LANDSAT_9': {
        "description": "Operational Land Imager 2 (OLI-2) and Thermal Infrared Sensor 2 (TIRS-2). Successor to Landsat 8.",
        "type": "Optical/Thermal",
        "resolution_nominal": "15m (Pan), 30m (MS), 100m (Thermal)",
        "revisit_interval": "16 days",
        "common_uses": "Land cover, change detection, vegetation, water, thermal mapping.",
        "use_categories": ["Land Cover", "Change Detection", "Vegetation Health", "Water Resources", "Agriculture"]
    },
    'LANDSAT_8': {
        "description": "Operational Land Imager (OLI) and Thermal Infrared Sensor (TIRS).",
        "type": "Optical/Thermal",
        "resolution_nominal": "15m (Pan), 30m (MS), 100m (Thermal)",
        "revisit_interval": "16 days",
        "common_uses": "Land cover, change detection, vegetation, water, thermal mapping.",
        "use_categories": ["Forest Monitoring", "Coastal Zones", "Urban Studies", "Glacier Change", "Burn Severity"]
    },
    'LANDSAT_7': {
        "description": "Enhanced Thematic Mapper Plus (ETM+). Scan Line Corrector (SLC) failed in 2003, resulting in data gaps for L1 products. L2 products are often gap-filled.",
        "type": "Optical/Thermal",
        "resolution_nominal": "15m (Pan), 30m (MS), 60m (Thermal)",
        "revisit_interval": "16 days",
        "common_uses": "Historical land studies, gap-filled products often used.",
        "use_categories": ["Historical Analysis", "Land Use Change", "Environmental Monitoring", "Geology", "Natural Hazards"]
    },
    'LANDSAT_5': {
        "description": "Thematic Mapper (TM). Longest-operating Earth-observing satellite.",
        "type": "Optical/Thermal",
        "resolution_nominal": "30m (MS), 120m (Thermal)",
        "revisit_interval": "16 days",
        "common_uses": "Historical land cover and change analysis.",
        "use_categories": ["Long-term Trends", "Deforestation", "Resource Management", "Ecosystem Dynamics", "Drought Monitoring"]
    },
    'LANDSAT_4': {
        "description": "Thematic Mapper (TM). Predecessor to Landsat 5.",
        "type": "Optical/Thermal",
        "resolution_nominal": "30m (MS), 120m (Thermal)",
        "revisit_interval": "16 days",
        "common_uses": "Early historical land studies.",
        "use_categories": ["Baseline Data", "Early Remote Sensing", "Land Management", "Hydrology", "Soil Mapping"]
    },
    'SENTINEL2': {
        "description": "Copernicus Sentinel-2 (MSI - MultiSpectral Instrument). Twin satellites (S2A & S2B). SR Harmonized product used.",
        "type": "Optical",
        "resolution_nominal": "10m, 20m, 60m (depending on band)",
        "revisit_interval": "~5 days (combined constellation at equator)",
        "common_uses": "Vegetation, land cover, agriculture, coastal monitoring, emergency mapping.",
        "use_categories": ["Precision Agriculture", "Forest Health", "Water Quality", "Disaster Response", "Urban Expansion"]
    },
    'VIIRS': {
        "description": "Visible Infrared Imaging Radiometer Suite (on Suomi NPP and JPSS satellites). Surface Reflectance (VNP09GA).",
        "type": "Optical/Thermal",
        "resolution_nominal": "375m, 750m (depending on band)",
        "revisit_interval": "Daily (global)",
        "common_uses": "Weather, climate, oceanography, vegetation, fire detection, aerosols, nighttime lights.",
        "use_categories": ["Active Fires", "Nighttime Lights", "Sea Surface Temp.", "Aerosol Optical Depth", "Snow/Ice Cover"]
    },
    'MODIS': {
        "description": "Moderate Resolution Imaging Spectroradiometer (on Terra and Aqua satellites). Surface Reflectance (MOD09GA/MYD09GA).",
        "type": "Optical/Thermal",
        "resolution_nominal": "250m, 500m, 1km (depending on band)",
        "revisit_interval": "Daily (global, combined)",
        "common_uses": "Global dynamics, land/ocean/atmosphere products, vegetation indices, surface temperature, cloud/aerosol properties.",
        "use_categories": ["Global Vegetation Index", "Cloud Masking", "Ocean Productivity", "Atmospheric Correction", "Land Surface Temp."]
    },
    'ERA5_TEMP': {
        "description": "ERA5-Land Daily Aggregated - ECMWF Climate Reanalysis. Provides mean 2m air temperature.",
        "type": "Reanalysis Model",
        "resolution_nominal": "0.1° x 0.1° (~9km)",
        "revisit_interval": "Daily (model output)",
        "common_uses": "Climate analysis, historical weather assessment, environmental modeling.",
        "use_categories": ["Climate Trends", "Weather Analysis", "Agricultural Modeling", "Hydrological Studies", "Environmental Science"]
    },
}

# Satellite categories for organization
SATELLITE_CATEGORIES = {
    "Landsat Program": ['LANDSAT_9', 'LANDSAT_8', 'LANDSAT_7', 'LANDSAT_5', 'LANDSAT_4'],
    "Copernicus Sentinel": ['SENTINEL2'],
    "NASA EOS & NOAA": ['MODIS', 'VIIRS'],
    "Gridded Climate Products": ['ERA5_TEMP']
}

# Available indices for analysis
AVAILABLE_INDICES = {
    "NDVI": {
        "name": "Normalized Difference Vegetation Index",
        "bands_needed": ["NIR", "Red"],
        "formula_desc": "(NIR - Red) / (NIR + Red)"
    },
    "EVI": {
        "name": "Enhanced Vegetation Index",
        "bands_needed": ["NIR", "Red", "Blue"],
        "formula_desc": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)"
    },
    "SAVI": {
        "name": "Soil Adjusted Vegetation Index",
        "bands_needed": ["NIR", "Red"],
        "formula_desc": "((NIR - Red) / (NIR + Red + L)) * (1 + L) (L=0.5)"
    },
    "NDWI_Gao": {
        "name": "Normalized Difference Water Index (Gao)",
        "bands_needed": ["NIR", "SWIR1"],
        "formula_desc": "(NIR - SWIR1) / (NIR + SWIR1)"
    },
    "MNDWI_Xu": {
        "name": "Modified Normalized Difference Water Index (Xu)",
        "bands_needed": ["Green", "SWIR1"],
        "formula_desc": "(Green - SWIR1) / (Green + SWIR1)"
    },
    "NDBI": {
        "name": "Normalized Difference Built-up Index",
        "bands_needed": ["SWIR1", "NIR"],
        "formula_desc": "(SWIR1 - NIR) / (SWIR1 + NIR)"
    },
}


class SatelliteInfoManager:
    """Centralized access to satellite sensor metadata and utilities."""
    def __init__(self):
        self._details = SATELLITE_DETAILS

    def get_available_sensors(self):
        """Return a list of available sensor names."""
        return list(self._details.keys())

    def get_sensor_details(self, sensor_name):
        """Return details dict for a given sensor name."""
        return self._details.get(sensor_name, {})

    def get_available_indices(self):
        """Return a dict of available indices per sensor (example structure)."""
        # This can be expanded as needed
        return {
            'LANDSAT_9': ['NDVI', 'EVI'],
            'LANDSAT_8': ['NDVI', 'EVI'],
            'SENTINEL_2': ['NDVI', 'EVI'],
            'ERA5_LAND': ['Temperature']
        }

    def get_satellite_categories(self):
        """Return a dict grouping sensors by category (example structure)."""
        return {
            'Optical': ['LANDSAT_9', 'LANDSAT_8', 'SENTINEL_2'],
            'Climate': ['ERA5_LAND']
        }

    def get_satellite_details(self, sensor_name: str) -> Dict[str, Any]:
        """Get detailed information for a satellite sensor."""
        return SATELLITE_DETAILS.get(sensor_name, {})
    
    def get_satellite_categories(self) -> Dict[str, List[str]]:
        """Get satellite categories and their sensors."""
        return SATELLITE_CATEGORIES
    
    def get_sensor_timeline(self, sensor_name: str) -> Tuple[str, str]:
        """Get start and end dates for a sensor."""
        return SENSOR_TIMELINE.get(sensor_name, (None, None))
    
    def get_data_collections(self, sensor_name: str) -> List[str]:
        """Get data collections for a sensor."""
        return DATA_COLLECTIONS.get(sensor_name, [])
    
    def is_sensor_available(self, sensor_name: str, target_date: datetime) -> bool:
        """Check if a sensor is available for a given date."""
        if sensor_name not in SENSOR_TIMELINE:
            return False
        
        start_date_str, end_date_str = SENSOR_TIMELINE[sensor_name]
        
        # Parse start date
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except (ValueError, TypeError):
            return False
        
        # Check if target date is after start date
        if target_date < start_date:
            return False
        
        # If no end date, sensor is still active
        if end_date_str is None:
            return True
        
        # Parse end date
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            return target_date <= end_date
        except (ValueError, TypeError):
            return True  # If end date parsing fails, assume still active
    
    def get_sensors_by_category(self, category: str) -> List[str]:
        """Get sensors in a specific category."""
        return SATELLITE_CATEGORIES.get(category, [])
    
    def get_sensor_resolution(self, sensor_name: str) -> str:
        """Get nominal resolution for a sensor."""
        details = self.get_satellite_details(sensor_name)
        return details.get('resolution_nominal', 'Unknown')
    
    def get_sensor_type(self, sensor_name: str) -> str:
        """Get sensor type (Optical, Thermal, etc.)."""
        details = self.get_satellite_details(sensor_name)
        return details.get('type', 'Unknown')
    
    def get_sensor_uses(self, sensor_name: str) -> List[str]:
        """Get common use categories for a sensor."""
        details = self.get_satellite_details(sensor_name)
        return details.get('use_categories', [])

# Usage:
# sat_manager = SatelliteInfoManager()
# sensors = sat_manager.get_available_sensors()
# details = sat_manager.get_sensor_details('LANDSAT_9') 