import re
import json
import jsonschema
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import threading
from collections import defaultdict

# Advanced validation imports
try:
    import cerberus
    CERBERUS_AVAILABLE = True
except ImportError:
    CERBERUS_AVAILABLE = False

try:
    from marshmallow import Schema, fields, ValidationError
    MARSHMALLOW_AVAILABLE = True
except ImportError:
    MARSHMALLOW_AVAILABLE = False

class DatasetSchema:
    """Advanced schema definition for dataset validation"""
    
    # JSON Schema for dataset validation
    JSON_SCHEMA = {
        "type": "object",
        "properties": {
            "title": {
                "type": "string",
                "minLength": 1,
                "maxLength": 500
            },
            "provider": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100
            },
            "description": {
                "type": "string",
                "maxLength": 2000
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": 50
            },
            "date_range": {
                "type": "string",
                "pattern": r"^\d{4}(-\d{2}(-\d{2})?)?(\s*to\s*\d{4}(-\d{2}(-\d{2})?)?)?$"
            },
            "source_url": {
                "type": "string",
                "format": "uri"
            },
            "confidence": {
                "type": "object",
                "properties": {
                    "title": {"type": "number", "minimum": 0, "maximum": 1},
                    "description": {"type": "number", "minimum": 0, "maximum": 1},
                    "provider": {"type": "number", "minimum": 0, "maximum": 1}
                }
            },
            "ml_classification": {
                "type": "object"
            },
            "validation_results": {
                "type": "object"
            }
        },
        "required": ["title", "source_url"]
    }
    
    # Cerberus schema (alternative validation)
    CERBERUS_SCHEMA = {
        'title': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 500,
            'required': True
        },
        'provider': {
            'type': 'string',
            'minlength': 1,
            'maxlength': 100
        },
        'description': {
            'type': 'string',
            'maxlength': 2000
        },
        'tags': {
            'type': 'list',
            'schema': {'type': 'string'},
            'maxlength': 50
        },
        'source_url': {
            'type': 'string',
            'regex': r'^https?://.+',
            'required': True
        },
        'confidence': {
            'type': 'dict',
            'schema': {
                'title': {'type': 'float', 'min': 0, 'max': 1},
                'description': {'type': 'float', 'min': 0, 'max': 1},
                'provider': {'type': 'float', 'min': 0, 'max': 1}
            }
        }
    }

class AdvancedValidator:
    """Advanced validation system with multiple validation methods"""
    
    def __init__(self):
        self.validation_cache = {}
        self.validation_stats = defaultdict(int)
        self.validation_lock = threading.Lock()
        
        # Known providers for validation
        self.known_providers = {
            'nasa', 'esa', 'usgs', 'noaa', 'copernicus', 'google', 'microsoft',
            'amazon', 'digitalglobe', 'planet', 'maxar', 'airbus'
        }
        
        # Known dataset types
        self.known_types = {
            'satellite', 'aerial', 'dem', 'climate', 'weather', 'ocean',
            'land_cover', 'vegetation', 'urban', 'geological', 'hydrological'
        }
        
        # Validation rules
        self.validation_rules = {
            'title_min_length': 3,
            'title_max_length': 500,
            'description_min_length': 10,
            'description_max_length': 2000,
            'max_tags': 50,
            'min_confidence': 0.1,
            'max_confidence': 1.0
        }
        
    def validate_dataset(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive dataset validation"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'score': 100.0,
            'validation_details': {},
            'schema_validation': {},
            'consistency_checks': {},
            'quality_checks': {}
        }
        
        try:
            # 1. Schema validation
            schema_result = self._validate_schema(data)
            validation_result['schema_validation'] = schema_result
            if not schema_result['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(schema_result['errors'])
                
            # 2. Data consistency checks
            consistency_result = self._check_consistency(data)
            validation_result['consistency_checks'] = consistency_result
            if not consistency_result['valid']:
                validation_result['warnings'].extend(consistency_result['warnings'])
                
            # 3. Quality checks
            quality_result = self._check_quality(data)
            validation_result['quality_checks'] = quality_result
            validation_result['score'] = quality_result['score']
            
            # 4. Business logic validation
            business_result = self._validate_business_logic(data)
            validation_result['business_validation'] = business_result
            if not business_result['valid']:
                validation_result['warnings'].extend(business_result['warnings'])
                
            # Update statistics
            with self.validation_lock:
                self.validation_stats['total_validations'] += 1
                if validation_result['valid']:
                    self.validation_stats['passed_validations'] += 1
                else:
                    self.validation_stats['failed_validations'] += 1
                    
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation error: {str(e)}")
            
        return validation_result
        
    def _validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data against schema"""
        result = {
            'valid': True,
            'errors': [],
            'method': 'unknown'
        }
        
        # Try JSON Schema validation
        try:
            jsonschema.validate(instance=data, schema=DatasetSchema.JSON_SCHEMA)
            result['method'] = 'json_schema'
            return result
        except jsonschema.ValidationError as e:
            result['errors'].append(f"JSON Schema: {str(e)}")
        except Exception as e:
            result['errors'].append(f"JSON Schema error: {str(e)}")
            
        # Try Cerberus validation
        if CERBERUS_AVAILABLE:
            try:
                from cerberus import Validator
                validator = Validator(DatasetSchema.CERBERUS_SCHEMA)
                if validator.validate(data):
                    result['method'] = 'cerberus'
                    result['valid'] = True
                    result['errors'] = []
                    return result
                else:
                    result['errors'].append(f"Cerberus: {validator.errors}")
            except Exception as e:
                result['errors'].append(f"Cerberus error: {str(e)}")
                
        # Try Marshmallow validation
        if MARSHMALLOW_AVAILABLE:
            try:
                schema_result = self._validate_with_marshmallow(data)
                if schema_result['valid']:
                    result['method'] = 'marshmallow'
                    result['valid'] = True
                    result['errors'] = []
                    return result
                else:
                    result['errors'].extend(schema_result['errors'])
            except Exception as e:
                result['errors'].append(f"Marshmallow error: {str(e)}")
                
        result['valid'] = False
        return result
        
    def _validate_with_marshmallow(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate using Marshmallow schema"""
        class DatasetMarshmallowSchema(Schema):
            title = fields.Str(required=True, validate=lambda x: len(x) >= 3)
            provider = fields.Str(validate=lambda x: len(x) >= 1 if x else True)
            description = fields.Str(validate=lambda x: len(x) <= 2000 if x else True)
            tags = fields.List(fields.Str(), validate=lambda x: len(x) <= 50 if x else True)
            source_url = fields.Url(required=True)
            confidence = fields.Dict(keys=fields.Str(), values=fields.Float())
            
        try:
            schema = DatasetMarshmallowSchema()
            schema.load(data)
            return {'valid': True, 'errors': []}
        except ValidationError as e:
            return {'valid': False, 'errors': [str(e)]}
            
    def _check_consistency(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data consistency"""
        result = {
            'valid': True,
            'warnings': [],
            'checks': {}
        }
        
        # Check URL consistency
        if 'source_url' in data:
            url_check = self._validate_url_consistency(data['source_url'])
            result['checks']['url_consistency'] = url_check
            if not url_check['valid']:
                result['warnings'].append(url_check['message'])
                
        # Check date consistency
        if 'date_range' in data:
            date_check = self._validate_date_consistency(data['date_range'])
            result['checks']['date_consistency'] = date_check
            if not date_check['valid']:
                result['warnings'].append(date_check['message'])
                
        # Check confidence consistency
        if 'confidence' in data:
            conf_check = self._validate_confidence_consistency(data['confidence'])
            result['checks']['confidence_consistency'] = conf_check
            if not conf_check['valid']:
                result['warnings'].append(conf_check['message'])
                
        return result
        
    def _validate_url_consistency(self, url: str) -> Dict[str, Any]:
        """Validate URL consistency"""
        if not url:
            return {'valid': False, 'message': 'URL is empty'}
            
        # Check URL format
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        if not re.match(url_pattern, url):
            return {'valid': False, 'message': 'Invalid URL format'}
            
        # Check for common URL issues
        if len(url) > 2048:
            return {'valid': False, 'message': 'URL too long'}
            
        return {'valid': True, 'message': 'URL is consistent'}
        
    def _validate_date_consistency(self, date_range: str) -> Dict[str, Any]:
        """Validate date range consistency"""
        if not date_range:
            return {'valid': True, 'message': 'No date range provided'}
            
        # Check date range format
        date_patterns = [
            r'^\d{4}$',  # Year only
            r'^\d{4}-\d{2}$',  # Year-Month
            r'^\d{4}-\d{2}-\d{2}$',  # Full date
            r'^\d{4}(-\d{2}(-\d{2})?)?\s*to\s*\d{4}(-\d{2}(-\d{2})?)?$'  # Range
        ]
        
        for pattern in date_patterns:
            if re.match(pattern, date_range):
                return {'valid': True, 'message': 'Date range format is valid'}
                
        return {'valid': False, 'message': 'Invalid date range format'}
        
    def _validate_confidence_consistency(self, confidence: Dict[str, float]) -> Dict[str, Any]:
        """Validate confidence scores consistency"""
        if not confidence:
            return {'valid': True, 'message': 'No confidence scores provided'}
            
        for key, value in confidence.items():
            if not isinstance(value, (int, float)):
                return {'valid': False, 'message': f'Invalid confidence type for {key}'}
            if value < 0 or value > 1:
                return {'valid': False, 'message': f'Confidence score out of range for {key}'}
                
        return {'valid': True, 'message': 'Confidence scores are consistent'}
        
    def _check_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check data quality"""
        score = 100.0
        issues = []
        
        # Title quality
        if 'title' in data:
            title = data['title']
            if len(title) < self.validation_rules['title_min_length']:
                score -= 10
                issues.append('Title too short')
            elif len(title) > self.validation_rules['title_max_length']:
                score -= 5
                issues.append('Title too long')
                
        # Description quality
        if 'description' in data:
            desc = data['description']
            if len(desc) < self.validation_rules['description_min_length']:
                score -= 15
                issues.append('Description too short')
            elif len(desc) > self.validation_rules['description_max_length']:
                score -= 10
                issues.append('Description too long')
                
        # Tags quality
        if 'tags' in data and data['tags']:
            if len(data['tags']) > self.validation_rules['max_tags']:
                score -= 5
                issues.append('Too many tags')
                
        # Provider quality
        if 'provider' in data:
            provider = data['provider'].lower() if data['provider'] else ''
            if provider and provider not in self.known_providers:
                score -= 5
                issues.append('Unknown provider')
                
        # Confidence quality
        if 'confidence' in data:
            conf = data['confidence']
            if isinstance(conf, dict):
                for key, value in conf.items():
                    if not isinstance(value, (int, float)) or value < 0 or value > 1:
                        score -= 10
                        issues.append('Invalid confidence scores')
                        break
                        
        return {
            'score': max(0, score),
            'issues': issues,
            'quality_level': 'High' if score >= 80 else 'Medium' if score >= 60 else 'Low'
        }
        
    def _validate_business_logic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate business logic rules"""
        warnings = []
        
        # Check for required fields
        required_fields = ['title', 'source_url']
        for field in required_fields:
            if field not in data or not data[field]:
                warnings.append(f'Missing required field: {field}')
                
        # Check for suspicious patterns
        if 'title' in data and data['title']:
            title = data['title'].lower()
            suspicious_patterns = ['test', 'example', 'sample', 'placeholder']
            if any(pattern in title for pattern in suspicious_patterns):
                warnings.append('Title contains suspicious patterns')
                
        # Check for duplicate content
        if 'description' in data and data['description']:
            desc = data['description']
            if len(desc) > 100 and len(set(desc.split())) < len(desc.split()) * 0.3:
                warnings.append('Description may contain repetitive content')
                
        return {
            'valid': len(warnings) == 0,
            'warnings': warnings
        }
        
    def validate_batch(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate a batch of datasets"""
        results = []
        batch_stats = {
            'total': len(data_list),
            'valid': 0,
            'invalid': 0,
            'avg_score': 0.0,
            'common_issues': defaultdict(int)
        }
        
        for data in data_list:
            result = self.validate_dataset(data)
            results.append(result)
            
            if result['valid']:
                batch_stats['valid'] += 1
            else:
                batch_stats['invalid'] += 1
                
            batch_stats['avg_score'] += result['score']
            
            # Count common issues
            for error in result['errors']:
                batch_stats['common_issues'][error] += 1
                
        if batch_stats['total'] > 0:
            batch_stats['avg_score'] /= batch_stats['total']
            
        return {
            'batch_stats': batch_stats,
            'individual_results': results
        }
        
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation statistics"""
        with self.validation_lock:
            stats = dict(self.validation_stats)
            
        if stats['total_validations'] > 0:
            stats['success_rate'] = (stats['passed_validations'] / stats['total_validations']) * 100
        else:
            stats['success_rate'] = 0
            
        return stats
        
    def clear_cache(self):
        """Clear validation cache"""
        with self.validation_lock:
            self.validation_cache.clear()
            
    def add_known_provider(self, provider: str):
        """Add a known provider"""
        self.known_providers.add(provider.lower())
        
    def add_known_type(self, dataset_type: str):
        """Add a known dataset type"""
        self.known_types.add(dataset_type.lower())

# Global validator instance
advanced_validator = AdvancedValidator() 