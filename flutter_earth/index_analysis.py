"""Index analysis module for Flutter Earth."""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import rasterio
from rasterio.merge import merge
import json
from pathlib import Path

from .errors import ProcessingError, ValidationError, handle_errors
from .types import ProcessingParams
from .config import config_manager


# Available indices for analysis
AVAILABLE_INDICES = {
    "NDVI": {
        "name": "Normalized Difference Vegetation Index",
        "bands_needed": ["NIR", "Red"],
        "formula_desc": "(NIR - Red) / (NIR + Red)",
        "formula": lambda nir, red: (nir - red) / (nir + red + 1e-8)
    },
    "EVI": {
        "name": "Enhanced Vegetation Index",
        "bands_needed": ["NIR", "Red", "Blue"],
        "formula_desc": "2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)",
        "formula": lambda nir, red, blue: 2.5 * (nir - red) / (nir + 6*red - 7.5*blue + 1)
    },
    "SAVI": {
        "name": "Soil Adjusted Vegetation Index",
        "bands_needed": ["NIR", "Red"],
        "formula_desc": "((NIR - Red) / (NIR + Red + L)) * (1 + L) (L=0.5)",
        "formula": lambda nir, red: ((nir - red) / (nir + red + 0.5)) * 1.5
    },
    "NDWI_Gao": {
        "name": "Normalized Difference Water Index (Gao)",
        "bands_needed": ["NIR", "SWIR1"],
        "formula_desc": "(NIR - SWIR1) / (NIR + SWIR1)",
        "formula": lambda nir, swir1: (nir - swir1) / (nir + swir1 + 1e-8)
    },
    "MNDWI_Xu": {
        "name": "Modified Normalized Difference Water Index (Xu)",
        "bands_needed": ["Green", "SWIR1"],
        "formula_desc": "(Green - SWIR1) / (Green + SWIR1)",
        "formula": lambda green, swir1: (green - swir1) / (green + swir1 + 1e-8)
    },
    "NDBI": {
        "name": "Normalized Difference Built-up Index",
        "bands_needed": ["SWIR1", "NIR"],
        "formula_desc": "(SWIR1 - NIR) / (SWIR1 + NIR)",
        "formula": lambda swir1, nir: (swir1 - nir) / (swir1 + nir + 1e-8)
    },
    "NDSI": {
        "name": "Normalized Difference Snow Index",
        "bands_needed": ["Green", "SWIR1"],
        "formula_desc": "(Green - SWIR1) / (Green + SWIR1)",
        "formula": lambda green, swir1: (green - swir1) / (green + swir1 + 1e-8)
    },
    "NDMI": {
        "name": "Normalized Difference Moisture Index",
        "bands_needed": ["NIR", "SWIR1"],
        "formula_desc": "(NIR - SWIR1) / (NIR + SWIR1)",
        "formula": lambda nir, swir1: (nir - swir1) / (nir + swir1 + 1e-8)
    }
}

# Band mapping for common satellite sensors
BAND_MAPPINGS = {
    "LANDSAT_8": {
        "NIR": 5, "Red": 4, "Blue": 2, "Green": 3, "SWIR1": 6, "SWIR2": 7
    },
    "LANDSAT_9": {
        "NIR": 5, "Red": 4, "Blue": 2, "Green": 3, "SWIR1": 6, "SWIR2": 7
    },
    "SENTINEL2": {
        "NIR": 8, "Red": 4, "Blue": 2, "Green": 3, "SWIR1": 11, "SWIR2": 12
    }
}


class IndexAnalyzer:
    """Handles index calculation for satellite imagery."""
    
    def __init__(self):
        """Initialize the index analyzer."""
        self.logger = logging.getLogger(__name__)
        self.current_task: Optional[str] = None
        self.cancel_requested = False
    
    def request_cancel(self) -> None:
        """Request cancellation of current processing task."""
        self.cancel_requested = True
        logging.info("Index analysis cancellation requested.")
    
    @handle_errors()
    def calculate_indices(
        self,
        input_files: List[str],
        output_dir: str,
        selected_indices: List[str],
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """Calculate selected indices for input raster files.
        
        Args:
            input_files: List of input raster file paths.
            output_dir: Output directory for index files.
            selected_indices: List of index names to calculate.
            progress_callback: Optional callback for progress updates.
        
        Returns:
            List of processing results.
        
        Raises:
            ProcessingError: If processing fails.
        """
        self.cancel_requested = False
        self.current_task = "Index Analysis"
        
        try:
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            results = []
            total_files = len(input_files)
            
            for i, input_file in enumerate(input_files):
                if self.cancel_requested:
                    logging.info("Index analysis cancelled.")
                    break
                
                try:
                    # Update progress
                    if progress_callback:
                        progress_callback(i, total_files)
                    
                    # Process file
                    file_results = self._process_single_file(
                        input_file, output_dir, selected_indices
                    )
                    results.extend(file_results)
                    
                except Exception as e:
                    logging.error(f"Error processing file {input_file}: {e}")
                    results.append({
                        'success': False,
                        'message': str(e),
                        'input_file': input_file,
                        'output_files': [],
                        'error': e
                    })
            
            return results
            
        finally:
            self.current_task = None
    
    def _process_single_file(
        self,
        input_file: str,
        output_dir: str,
        selected_indices: List[str]
    ) -> List[Dict[str, Any]]:
        """Process a single input file for index calculation.
        
        Args:
            input_file: Input raster file path.
            output_dir: Output directory.
            selected_indices: List of indices to calculate.
        
        Returns:
            List of processing results for this file.
        """
        results = []
        
        try:
            with rasterio.open(input_file) as src:
                # Detect sensor type from filename or metadata
                sensor_type = self._detect_sensor_type(input_file, src)
                
                # Get band mapping for this sensor
                band_mapping = BAND_MAPPINGS.get(sensor_type, {})
                
                if not band_mapping:
                    raise ProcessingError(
                        f"No band mapping available for sensor type: {sensor_type}"
                    )
                
                # Calculate each selected index
                for index_name in selected_indices:
                    if index_name not in AVAILABLE_INDICES:
                        logging.warning(f"Unknown index: {index_name}")
                        continue
                    
                    try:
                        result = self._calculate_single_index(
                            src, index_name, band_mapping, input_file, output_dir
                        )
                        results.append(result)
                    except Exception as e:
                        logging.error(f"Error calculating {index_name}: {e}")
                        results.append({
                            'success': False,
                            'message': str(e),
                            'index_name': index_name,
                            'input_file': input_file,
                            'output_file': None,
                            'error': e
                        })
        
        except Exception as e:
            raise ProcessingError(
                f"Failed to process file {input_file}",
                details={"error": str(e)}
            )
        
        return results
    
    def _detect_sensor_type(self, filepath: str, src: rasterio.DatasetReader) -> str:
        """Detect sensor type from filename or metadata.
        
        Args:
            filepath: Input file path.
            src: Rasterio dataset reader.
        
        Returns:
            Detected sensor type.
        """
        filename = os.path.basename(filepath).lower()
        
        # Try to detect from filename
        if 'landsat8' in filename or 'l8' in filename:
            return "LANDSAT_8"
        elif 'landsat9' in filename or 'l9' in filename:
            return "LANDSAT_9"
        elif 'sentinel2' in filename or 's2' in filename:
            return "SENTINEL2"
        
        # Try to detect from band count
        band_count = src.count
        
        if band_count >= 11:  # Sentinel-2 has 13 bands
            return "SENTINEL2"
        elif band_count >= 7:  # Landsat has 7-11 bands
            return "LANDSAT_8"  # Default to Landsat 8
        
        # Default fallback
        return "LANDSAT_8"
    
    def _calculate_single_index(
        self,
        src: rasterio.DatasetReader,
        index_name: str,
        band_mapping: Dict[str, int],
        input_file: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """Calculate a single index.
        
        Args:
            src: Rasterio dataset reader.
            index_name: Name of the index to calculate.
            band_mapping: Mapping of band names to band numbers.
            input_file: Input file path.
            output_dir: Output directory.
        
        Returns:
            Processing result.
        """
        index_info = AVAILABLE_INDICES[index_name]
        required_bands = index_info["bands_needed"]
        formula = index_info["formula"]
        
        # Check if we have the required bands
        missing_bands = []
        band_data = {}
        
        for band_name in required_bands:
            if band_name not in band_mapping:
                missing_bands.append(band_name)
            else:
                band_num = band_mapping[band_name]
                if band_num > src.count:
                    missing_bands.append(band_name)
                else:
                    band_data[band_name] = src.read(band_num).astype(np.float32)
        
        if missing_bands:
            raise ProcessingError(
                f"Missing required bands for {index_name}: {missing_bands}"
            )
        
        # Calculate the index
        try:
            if len(required_bands) == 2:
                result = formula(band_data[required_bands[0]], band_data[required_bands[1]])
            elif len(required_bands) == 3:
                result = formula(
                    band_data[required_bands[0]], 
                    band_data[required_bands[1]], 
                    band_data[required_bands[2]]
                )
            else:
                raise ProcessingError(f"Unsupported number of bands for {index_name}")
            
            # Handle invalid values
            result = np.where(np.isnan(result), 0, result)
            result = np.where(np.isinf(result), 0, result)
            
            # Save the result
            output_filename = f"{Path(input_file).stem}_{index_name}.tif"
            output_path = os.path.join(output_dir, output_filename)
            
            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=src.height,
                width=src.width,
                count=1,
                dtype=result.dtype,
                crs=src.crs,
                transform=src.transform,
                nodata=0
            ) as dst:
                dst.write(result, 1)
            
            return {
                'success': True,
                'message': f"Successfully calculated {index_name}",
                'index_name': index_name,
                'input_file': input_file,
                'output_file': output_path,
                'error': None
            }
            
        except Exception as e:
            raise ProcessingError(
                f"Error calculating {index_name}",
                details={"error": str(e)}
            )
    
    def get_available_indices(self) -> Dict[str, Dict[str, Any]]:
        """Get available indices information.
        
        Returns:
            Dictionary of available indices.
        """
        return AVAILABLE_INDICES.copy()
    
    def get_band_mappings(self) -> Dict[str, Dict[str, int]]:
        """Get band mappings for different sensors.
        
        Returns:
            Dictionary of band mappings.
        """
        return BAND_MAPPINGS.copy()


# Global instance
index_analyzer = IndexAnalyzer() 