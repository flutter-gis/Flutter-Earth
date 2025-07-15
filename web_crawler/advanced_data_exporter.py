import json
import csv
import xml.etree.ElementTree as ET
import yaml
import sqlite3
import threading
import time
from datetime import datetime
from pathlib import Path
import zipfile
import tempfile
import shutil

# Advanced export formats
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False

try:
    import avro.schema
    from avro.datafile import DataFileWriter
    from avro.io import DatumWriter
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

class AdvancedDataExporter:
    """Advanced data export system with multiple formats and database integration"""
    
    def __init__(self, output_dir="exported_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.export_lock = threading.Lock()
        
        # Database connection
        self.db_path = self.output_dir / "crawler_data.db"
        self.db_conn = None
        self._init_database()
        
        # Export statistics
        self.export_stats = {
            'total_exports': 0,
            'formats_exported': {},
            'last_export': None,
            'total_records': 0
        }
        
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            self.db_conn = sqlite3.connect(str(self.db_path))
            cursor = self.db_conn.cursor()
            
            # Create datasets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    provider TEXT,
                    description TEXT,
                    tags TEXT,
                    date_range TEXT,
                    spatial_coverage TEXT,
                    temporal_coverage TEXT,
                    source_url TEXT,
                    extraction_time TIMESTAMP,
                    confidence_score REAL,
                    ml_classification TEXT,
                    validation_results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER,
                    key TEXT,
                    value TEXT,
                    FOREIGN KEY (dataset_id) REFERENCES datasets (id)
                )
            ''')
            
            # Create export_log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS export_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    export_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    format TEXT,
                    record_count INTEGER,
                    file_path TEXT,
                    success BOOLEAN,
                    error_message TEXT
                )
            ''')
            
            self.db_conn.commit()
            print("✓ Database initialized successfully")
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
            self.db_conn = None
            
    def export_data(self, data, formats=None, include_metadata=True):
        """Export data in multiple formats"""
        if formats is None:
            formats = ['json', 'csv', 'sqlite']
            
        if PANDAS_AVAILABLE:
            formats.append('parquet')
        if AVRO_AVAILABLE:
            formats.append('avro')
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_results = {}
        
        with self.export_lock:
            for format_type in formats:
                try:
                    if format_type == 'json':
                        result = self._export_json(data, timestamp)
                    elif format_type == 'csv':
                        result = self._export_csv(data, timestamp)
                    elif format_type == 'sqlite':
                        result = self._export_sqlite(data)
                    elif format_type == 'parquet' and PANDAS_AVAILABLE:
                        result = self._export_parquet(data, timestamp)
                    elif format_type == 'avro' and AVRO_AVAILABLE:
                        result = self._export_avro(data, timestamp)
                    elif format_type == 'xml':
                        result = self._export_xml(data, timestamp)
                    elif format_type == 'yaml':
                        result = self._export_yaml(data, timestamp)
                    elif format_type == 'zip':
                        result = self._export_zip(data, timestamp)
                    else:
                        result = {'success': False, 'error': f'Format {format_type} not supported'}
                        
                    export_results[format_type] = result
                    
                    # Update statistics
                    if result.get('success'):
                        self.export_stats['total_exports'] += 1
                        self.export_stats['formats_exported'][format_type] = self.export_stats['formats_exported'].get(format_type, 0) + 1
                        self.export_stats['total_records'] += len(data)
                        self.export_stats['last_export'] = datetime.now().isoformat()
                        
                except Exception as e:
                    export_results[format_type] = {
                        'success': False,
                        'error': str(e)
                    }
                    
        return export_results
        
    def _export_json(self, data, timestamp):
        """Export to JSON format"""
        filename = self.output_dir / f"crawler_data_{timestamp}.json"
        
        export_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'record_count': len(data),
                'format': 'json'
            },
            'data': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            
        return {
            'success': True,
            'file_path': str(filename),
            'record_count': len(data),
            'file_size_mb': filename.stat().st_size / (1024 * 1024)
        }
        
    def _export_csv(self, data, timestamp):
        """Export to CSV format"""
        if not data:
            return {'success': False, 'error': 'No data to export'}
            
        filename = self.output_dir / f"crawler_data_{timestamp}.csv"
        
        # Flatten nested data for CSV
        flattened_data = []
        for item in data:
            flat_item = {}
            for key, value in item.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        flat_item[f"{key}_{sub_key}"] = json.dumps(sub_value) if isinstance(sub_value, (dict, list)) else sub_value
                elif isinstance(value, list):
                    flat_item[key] = json.dumps(value)
                else:
                    flat_item[key] = value
            flattened_data.append(flat_item)
            
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
                
        return {
            'success': True,
            'file_path': str(filename),
            'record_count': len(data),
            'file_size_mb': filename.stat().st_size / (1024 * 1024)
        }
        
    def _export_sqlite(self, data):
        """Export to SQLite database"""
        if not self.db_conn or not data:
            return {'success': False, 'error': 'Database not available or no data'}
            
        try:
            cursor = self.db_conn.cursor()
            inserted_count = 0
            
            for item in data:
                # Insert main dataset record
                cursor.execute('''
                    INSERT INTO datasets (
                        title, provider, description, tags, date_range,
                        spatial_coverage, temporal_coverage, source_url,
                        extraction_time, confidence_score, ml_classification,
                        validation_results
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('title', ''),
                    item.get('provider', ''),
                    item.get('description', ''),
                    json.dumps(item.get('tags', [])),
                    item.get('date_range', ''),
                    item.get('spatial_coverage', ''),
                    item.get('temporal_coverage', ''),
                    item.get('source_url', ''),
                    item.get('extraction_time', datetime.now().isoformat()),
                    item.get('confidence_score', 0.0),
                    json.dumps(item.get('ml_classification', {})),
                    json.dumps(item.get('validation_results', {}))
                ))
                
                dataset_id = cursor.lastrowid
                inserted_count += 1
                
                # Insert metadata
                for key, value in item.items():
                    if key not in ['title', 'provider', 'description', 'tags', 'date_range',
                                 'spatial_coverage', 'temporal_coverage', 'source_url',
                                 'extraction_time', 'confidence_score', 'ml_classification',
                                 'validation_results']:
                        cursor.execute('''
                            INSERT INTO metadata (dataset_id, key, value)
                            VALUES (?, ?, ?)
                        ''', (dataset_id, key, json.dumps(value)))
                        
            self.db_conn.commit()
            
            return {
                'success': True,
                'file_path': str(self.db_path),
                'record_count': inserted_count,
                'file_size_mb': self.db_path.stat().st_size / (1024 * 1024)
            }
            
        except Exception as e:
            self.db_conn.rollback()
            return {'success': False, 'error': str(e)}
            
    def _export_parquet(self, data, timestamp):
        """Export to Parquet format"""
        if not PANDAS_AVAILABLE:
            return {'success': False, 'error': 'Pandas not available'}
            
        filename = self.output_dir / f"crawler_data_{timestamp}.parquet"
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Write to parquet
        df.to_parquet(filename, index=False)
        
        return {
            'success': True,
            'file_path': str(filename),
            'record_count': len(data),
            'file_size_mb': filename.stat().st_size / (1024 * 1024)
        }
        
    def _export_avro(self, data, timestamp):
        """Export to Avro format"""
        if not AVRO_AVAILABLE:
            return {'success': False, 'error': 'Avro not available'}
            
        filename = self.output_dir / f"crawler_data_{timestamp}.avro"
        
        # Define Avro schema
        schema = {
            "type": "record",
            "name": "Dataset",
            "fields": [
                {"name": "title", "type": ["string", "null"]},
                {"name": "provider", "type": ["string", "null"]},
                {"name": "description", "type": ["string", "null"]},
                {"name": "tags", "type": {"type": "array", "items": "string"}},
                {"name": "source_url", "type": ["string", "null"]},
                {"name": "extraction_time", "type": ["string", "null"]},
                {"name": "confidence_score", "type": ["double", "null"]}
            ]
        }
        
        avro_schema = avro.schema.parse(json.dumps(schema))
        
        with open(filename, 'wb') as f:
            with DataFileWriter(f, DatumWriter(), avro_schema) as writer:
                for item in data:
                    writer.append({
                        'title': item.get('title'),
                        'provider': item.get('provider'),
                        'description': item.get('description'),
                        'tags': item.get('tags', []),
                        'source_url': item.get('source_url'),
                        'extraction_time': item.get('extraction_time'),
                        'confidence_score': item.get('confidence_score', 0.0)
                    })
                    
        return {
            'success': True,
            'file_path': str(filename),
            'record_count': len(data),
            'file_size_mb': filename.stat().st_size / (1024 * 1024)
        }
        
    def _export_xml(self, data, timestamp):
        """Export to XML format"""
        filename = self.output_dir / f"crawler_data_{timestamp}.xml"
        
        root = ET.Element("crawler_data")
        root.set("timestamp", datetime.now().isoformat())
        root.set("record_count", str(len(data)))
        
        for item in data:
            dataset_elem = ET.SubElement(root, "dataset")
            for key, value in item.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                elem = ET.SubElement(dataset_elem, key)
                elem.text = str(value) if value is not None else ""
                
        tree = ET.ElementTree(root)
        tree.write(filename, encoding='utf-8', xml_declaration=True)
        
        return {
            'success': True,
            'file_path': str(filename),
            'record_count': len(data),
            'file_size_mb': filename.stat().st_size / (1024 * 1024)
        }
        
    def _export_yaml(self, data, timestamp):
        """Export to YAML format"""
        filename = self.output_dir / f"crawler_data_{timestamp}.yaml"
        
        export_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'record_count': len(data),
                'format': 'yaml'
            },
            'data': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True)
            
        return {
            'success': True,
            'file_path': str(filename),
            'record_count': len(data),
            'file_size_mb': filename.stat().st_size / (1024 * 1024)
        }
        
    def _export_zip(self, data, timestamp):
        """Export as ZIP with multiple formats"""
        zip_filename = self.output_dir / f"crawler_data_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add JSON file
            json_data = self._export_json(data, timestamp)
            if json_data['success']:
                zipf.write(json_data['file_path'], 'data.json')
                Path(json_data['file_path']).unlink()  # Remove temp file
                
            # Add CSV file
            csv_data = self._export_csv(data, timestamp)
            if csv_data['success']:
                zipf.write(csv_data['file_path'], 'data.csv')
                Path(csv_data['file_path']).unlink()  # Remove temp file
                
        return {
            'success': True,
            'file_path': str(zip_filename),
            'record_count': len(data),
            'file_size_mb': zip_filename.stat().st_size / (1024 * 1024)
        }
        
    def get_export_statistics(self):
        """Get export statistics"""
        return self.export_stats.copy()
        
    def get_database_stats(self):
        """Get database statistics"""
        if not self.db_conn:
            return None
            
        cursor = self.db_conn.cursor()
        
        # Get record counts
        cursor.execute("SELECT COUNT(*) FROM datasets")
        dataset_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM metadata")
        metadata_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM export_log")
        export_count = cursor.fetchone()[0]
        
        # Get recent exports
        cursor.execute("""
            SELECT format, record_count, export_time, success 
            FROM export_log 
            ORDER BY export_time DESC 
            LIMIT 10
        """)
        recent_exports = cursor.fetchall()
        
        return {
            'dataset_count': dataset_count,
            'metadata_count': metadata_count,
            'export_count': export_count,
            'recent_exports': recent_exports,
            'database_size_mb': self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
        }
        
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()

# Global exporter instance
data_exporter = AdvancedDataExporter() 