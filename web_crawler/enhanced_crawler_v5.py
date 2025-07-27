#!/usr/bin/env python3
"""
Enhanced Earth Engine Web Crawler v5.0
Advanced AI-powered data extraction and classification system
"""

import sys
import os
import json
import time
import threading
import asyncio
import aiohttp
import aiofiles
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import hashlib
import pickle
import gzip
import logging
from pathlib import Path

# Core imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs
import re
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Advanced ML imports
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        AutoModelForTokenClassification, pipeline,
        DistilBertTokenizer, DistilBertForSequenceClassification,
        T5Tokenizer, T5ForConditionalGeneration
    )
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    import sklearn
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import SVC
    from sklearn.cluster import KMeans
    from sklearn.decomposition import LatentDirichletAllocation
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Geospatial imports
try:
    from geopy.geocoders import Nominatim, ArcGIS
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False

# Image processing
try:
    import cv2
    import numpy as np
    from PIL import Image, ImageEnhance
    import pytesseract
    IMAGE_PROCESSING_AVAILABLE = True
except ImportError:
    IMAGE_PROCESSING_AVAILABLE = False

# Data processing
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# Configuration
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

@dataclass
class DatasetMetadata:
    """Structured dataset metadata"""
    id: str
    title: str
    description: str
    provider: str
    tags: List[str]
    spatial_coverage: Dict[str, Any]
    temporal_coverage: Dict[str, Any]
    bands: List[Dict[str, Any]]
    resolution: Dict[str, Any]
    thumbnail_url: str
    source_url: str
    citation: str
    terms_of_use: str
    data_type: str
    quality_score: float
    confidence_score: float
    extraction_timestamp: datetime
    ml_classification: Dict[str, Any]
    validation_results: Dict[str, Any]
    enhanced_features: Dict[str, Any]

class AdvancedAIClassifier:
    """Advanced AI-powered classification system"""
    
    def __init__(self, cache_dir: str = "ai_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.models = {}
        self.classifiers = {}
        self.vectorizers = {}
        
        # Classification categories
        self.categories = {
            'satellite_imagery': ['landsat', 'sentinel', 'modis', 'aster', 'spot', 'pleiades'],
            'aerial_photography': ['aerial', 'drone', 'uav', 'airborne', 'photogrammetry'],
            'climate_data': ['climate', 'weather', 'temperature', 'precipitation', 'atmospheric'],
            'terrain_data': ['dem', 'elevation', 'terrain', 'topography', 'slope'],
            'vegetation_data': ['vegetation', 'forest', 'crop', 'agriculture', 'ndvi', 'evi'],
            'water_data': ['water', 'ocean', 'river', 'lake', 'coastal', 'marine'],
            'urban_data': ['urban', 'city', 'building', 'infrastructure', 'population'],
            'geological_data': ['geology', 'mineral', 'rock', 'soil', 'geological'],
            'atmospheric_data': ['atmosphere', 'air_quality', 'pollution', 'aerosol'],
            'cryosphere_data': ['ice', 'snow', 'glacier', 'polar', 'arctic', 'antarctic'],
            'oceanographic_data': ['ocean', 'marine', 'sea', 'current', 'salinity'],
            'disaster_data': ['disaster', 'emergency', 'flood', 'fire', 'earthquake']
        }
        
        self._load_models()
    
    def _load_models(self):
        """Load AI models asynchronously"""
        if TRANSFORMERS_AVAILABLE:
            self._load_transformer_models()
        
        if SPACY_AVAILABLE:
            self._load_spacy_models()
        
        if SKLEARN_AVAILABLE:
            self._load_sklearn_models()
    
    def _load_transformer_models(self):
        """Load transformer-based models"""
        try:
            # Load DistilBERT for text classification
            model_name = "distilbert-base-uncased"
            cache_path = self.cache_dir / f"{model_name}_classifier.pkl"
            
            if cache_path.exists():
                with open(cache_path, 'rb') as f:
                    self.models['distilbert'] = pickle.load(f)
            else:
                tokenizer = DistilBertTokenizer.from_pretrained(model_name)
                model = DistilBertForSequenceClassification.from_pretrained(
                    model_name, num_labels=len(self.categories)
                )
                classifier = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1  # CPU
                )
                self.models['distilbert'] = classifier
                
                # Cache the model
                with open(cache_path, 'wb') as f:
                    pickle.dump(classifier, f)
            
            # Load T5 for text generation and summarization
            t5_model = "t5-small"
            t5_cache_path = self.cache_dir / f"{t5_model}_generator.pkl"
            
            if t5_cache_path.exists():
                with open(t5_cache_path, 'rb') as f:
                    self.models['t5'] = pickle.load(f)
            else:
                t5_tokenizer = T5Tokenizer.from_pretrained(t5_model)
                t5_model_obj = T5ForConditionalGeneration.from_pretrained(t5_model)
                self.models['t5'] = (t5_tokenizer, t5_model_obj)
                
                with open(t5_cache_path, 'wb') as f:
                    pickle.dump((t5_tokenizer, t5_model_obj), f)
                    
        except Exception as e:
            print(f"Warning: Failed to load transformer models: {e}")
    
    def _load_spacy_models(self):
        """Load spaCy models for NER and text processing"""
        try:
            # Load English model
            self.models['spacy'] = spacy.load("en_core_web_sm")
        except Exception as e:
            print(f"Warning: Failed to load spaCy model: {e}")
    
    def _load_sklearn_models(self):
        """Load scikit-learn models for traditional ML"""
        try:
            # TF-IDF vectorizer
            self.vectorizers['tfidf'] = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            # Multiple classifiers for ensemble
            self.classifiers['random_forest'] = RandomForestClassifier(n_estimators=100)
            self.classifiers['gradient_boosting'] = GradientBoostingClassifier(n_estimators=100)
            self.classifiers['naive_bayes'] = MultinomialNB()
            self.classifiers['svm'] = SVC(probability=True)
            
        except Exception as e:
            print(f"Warning: Failed to load sklearn models: {e}")
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """Advanced text classification using multiple models"""
        results = {
            'bert_classification': None,
            'spacy_entities': None,
            'sklearn_ensemble': None,
            'rule_based': None,
            'final_classification': None,
            'confidence': 0.0
        }
        
        # BERT classification
        if 'distilbert' in self.models:
            try:
                bert_result = self.models['distilbert'](
                    text[:512],  # Limit length
                    truncation=True,
                    return_all_scores=True
                )
                results['bert_classification'] = bert_result
            except Exception as e:
                print(f"BERT classification failed: {e}")
        
        # spaCy NER
        if 'spacy' in self.models:
            try:
                doc = self.models['spacy'](text[:1000])
                entities = {}
                for ent in doc.ents:
                    if ent.label_ not in entities:
                        entities[ent.label_] = []
                    entities[ent.label_].append(ent.text)
                results['spacy_entities'] = entities
            except Exception as e:
                print(f"spaCy NER failed: {e}")
        
        # Rule-based classification
        results['rule_based'] = self._rule_based_classification(text)
        
        # Ensemble classification
        results['sklearn_ensemble'] = self._ensemble_classification(text)
        
        # Final classification with confidence
        results['final_classification'] = self._combine_classifications(results)
        
        return results
    
    def _rule_based_classification(self, text: str) -> Dict[str, Any]:
        """Rule-based classification using keyword matching"""
        text_lower = text.lower()
        scores = {}
        
        for category, keywords in self.categories.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score / len(keywords)
        
        if scores:
            best_category = max(scores, key=scores.get)
            return {
                'category': best_category,
                'confidence': min(scores[best_category], 1.0),
                'scores': scores
            }
        
        return {'category': 'general_data', 'confidence': 0.5, 'scores': {}}
    
    def _ensemble_classification(self, text: str) -> Dict[str, Any]:
        """Ensemble classification using multiple sklearn models"""
        if not SKLEARN_AVAILABLE or 'tfidf' not in self.vectorizers:
            return None
        
        try:
            # Vectorize text
            X = self.vectorizers['tfidf'].transform([text])
            
            # Get predictions from all classifiers
            predictions = {}
            for name, classifier in self.classifiers.items():
                try:
                    pred = classifier.predict(X)[0]
                    prob = classifier.predict_proba(X)[0]
                    predictions[name] = {
                        'prediction': pred,
                        'confidence': max(prob)
                    }
                except Exception as e:
                    print(f"Classifier {name} failed: {e}")
            
            # Combine predictions (simple voting)
            if predictions:
                categories = list(predictions.keys())
                votes = {}
                for pred in predictions.values():
                    cat = pred['prediction']
                    votes[cat] = votes.get(cat, 0) + 1
                
                if votes:
                    best_category = max(votes, key=votes.get)
                    confidence = votes[best_category] / len(predictions)
                    return {
                        'category': best_category,
                        'confidence': confidence,
                        'predictions': predictions
                    }
        
        except Exception as e:
            print(f"Ensemble classification failed: {e}")
        
        return None
    
    def _combine_classifications(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine multiple classification results"""
        classifications = []
        weights = []
        
        # Add rule-based classification
        if results['rule_based']:
            classifications.append(results['rule_based']['category'])
            weights.append(results['rule_based']['confidence'] * 0.3)
        
        # Add ensemble classification
        if results['sklearn_ensemble']:
            classifications.append(results['sklearn_ensemble']['category'])
            weights.append(results['sklearn_ensemble']['confidence'] * 0.4)
        
        # Add BERT classification
        if results['bert_classification']:
            bert_scores = results['bert_classification'][0]
            if bert_scores:
                best_bert = max(bert_scores, key=lambda x: x['score'])
                classifications.append(best_bert['label'])
                weights.append(best_bert['score'] * 0.3)
        
        if classifications and weights:
            # Weighted voting
            category_scores = {}
            for cat, weight in zip(classifications, weights):
                category_scores[cat] = category_scores.get(cat, 0) + weight
            
            best_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[best_category] / sum(weights)
            
            return {
                'category': best_category,
                'confidence': confidence,
                'method': 'ensemble',
                'contributions': dict(zip(classifications, weights))
            }
        
        # Fallback
        return {
            'category': 'general_data',
            'confidence': 0.5,
            'method': 'fallback'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = {}
        
        if 'spacy' in self.models:
            try:
                doc = self.models['spacy'](text[:1000])
                for ent in doc.ents:
                    if ent.label_ not in entities:
                        entities[ent.label_] = []
                    if ent.text not in entities[ent.label_]:
                        entities[ent.label_].append(ent.text)
            except Exception as e:
                print(f"Entity extraction failed: {e}")
        
        return entities
    
    def generate_summary(self, text: str, max_length: int = 150) -> str:
        """Generate text summary using T5"""
        if 't5' not in self.models:
            return text[:max_length] + "..." if len(text) > max_length else text
        
        try:
            tokenizer, model = self.models['t5']
            
            # Prepare input
            input_text = f"summarize: {text[:1000]}"
            inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate summary
            summary_ids = model.generate(
                inputs["input_ids"],
                max_length=max_length,
                min_length=30,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )
            
            summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            return summary
            
        except Exception as e:
            print(f"Summary generation failed: {e}")
            return text[:max_length] + "..." if len(text) > max_length else text

class AdvancedDataValidator:
    """Advanced data validation and quality assessment"""
    
    def __init__(self):
        self.geocoder = None
        if GEOPY_AVAILABLE:
            try:
                self.geocoder = Nominatim(user_agent="earth_engine_crawler_v5")
            except Exception as e:
                print(f"Geocoder initialization failed: {e}")
        
        # Validation rules
        self.validation_rules = {
            'spatial': {
                'max_bbox_size': 360,
                'min_coordinate_precision': 2
            },
            'temporal': {
                'min_year': 1970,
                'max_year': 2030,
                'max_date_range': 50  # years
            },
            'quality': {
                'min_description_length': 10,
                'max_title_length': 200,
                'min_confidence': 0.3
            }
        }
    
    def validate_dataset(self, dataset: DatasetMetadata) -> Dict[str, Any]:
        """Comprehensive dataset validation"""
        validation_results = {
            'spatial': self._validate_spatial_data(dataset),
            'temporal': self._validate_temporal_data(dataset),
            'quality': self._validate_data_quality(dataset),
            'consistency': self._validate_consistency(dataset),
            'overall_score': 0.0,
            'issues': []
        }
        
        # Calculate overall score
        scores = [
            validation_results['spatial']['score'],
            validation_results['temporal']['score'],
            validation_results['quality']['score'],
            validation_results['consistency']['score']
        ]
        
        validation_results['overall_score'] = sum(scores) / len(scores)
        
        return validation_results
    
    def _validate_spatial_data(self, dataset: DatasetMetadata) -> Dict[str, Any]:
        """Validate spatial coverage data"""
        result = {'valid': True, 'score': 1.0, 'issues': []}
        
        if not dataset.spatial_coverage:
            result['valid'] = False
            result['score'] = 0.0
            result['issues'].append('No spatial coverage information')
            return result
        
        # Validate coordinates
        if 'bbox' in dataset.spatial_coverage:
            bbox = dataset.spatial_coverage['bbox']
            if len(bbox) != 4:
                result['issues'].append('Invalid bbox format')
                result['score'] *= 0.8
            
            # Check bbox size
            if len(bbox) == 4:
                width = abs(bbox[2] - bbox[0])
                height = abs(bbox[3] - bbox[1])
                if width > self.validation_rules['spatial']['max_bbox_size']:
                    result['issues'].append('Bbox too large')
                    result['score'] *= 0.7
        
        return result
    
    def _validate_temporal_data(self, dataset: DatasetMetadata) -> Dict[str, Any]:
        """Validate temporal coverage data"""
        result = {'valid': True, 'score': 1.0, 'issues': []}
        
        if not dataset.temporal_coverage:
            result['valid'] = False
            result['score'] = 0.0
            result['issues'].append('No temporal coverage information')
            return result
        
        # Validate date ranges
        if 'start_date' in dataset.temporal_coverage and 'end_date' in dataset.temporal_coverage:
            try:
                start_date = datetime.fromisoformat(dataset.temporal_coverage['start_date'])
                end_date = datetime.fromisoformat(dataset.temporal_coverage['end_date'])
                
                if start_date.year < self.validation_rules['temporal']['min_year']:
                    result['issues'].append('Start date too early')
                    result['score'] *= 0.8
                
                if end_date.year > self.validation_rules['temporal']['max_year']:
                    result['issues'].append('End date too late')
                    result['score'] *= 0.8
                
                date_range = end_date.year - start_date.year
                if date_range > self.validation_rules['temporal']['max_date_range']:
                    result['issues'].append('Date range too large')
                    result['score'] *= 0.9
                    
            except ValueError:
                result['issues'].append('Invalid date format')
                result['score'] *= 0.5
        
        return result
    
    def _validate_data_quality(self, dataset: DatasetMetadata) -> Dict[str, Any]:
        """Validate data quality metrics"""
        result = {'valid': True, 'score': 1.0, 'issues': []}
        
        # Check description length
        if len(dataset.description) < self.validation_rules['quality']['min_description_length']:
            result['issues'].append('Description too short')
            result['score'] *= 0.8
        
        # Check title length
        if len(dataset.title) > self.validation_rules['quality']['max_title_length']:
            result['issues'].append('Title too long')
            result['score'] *= 0.9
        
        # Check confidence score
        if dataset.confidence_score < self.validation_rules['quality']['min_confidence']:
            result['issues'].append('Low confidence score')
            result['score'] *= 0.7
        
        return result
    
    def _validate_consistency(self, dataset: DatasetMetadata) -> Dict[str, Any]:
        """Validate data consistency"""
        result = {'valid': True, 'score': 1.0, 'issues': []}
        
        # Check for required fields
        required_fields = ['title', 'description', 'provider']
        for field in required_fields:
            if not getattr(dataset, field):
                result['issues'].append(f'Missing required field: {field}')
                result['score'] *= 0.8
        
        # Check for data type consistency
        if dataset.data_type and dataset.tags:
            type_in_tags = any(dataset.data_type.lower() in tag.lower() for tag in dataset.tags)
            if not type_in_tags:
                result['issues'].append('Data type not reflected in tags')
                result['score'] *= 0.9
        
        return result

class AdvancedDataExtractor:
    """Advanced data extraction with AI enhancement"""
    
    def __init__(self, ai_classifier: AdvancedAIClassifier, validator: AdvancedDataValidator):
        self.ai_classifier = ai_classifier
        self.validator = validator
        
        # Extraction patterns
        self.patterns = {
            'satellite_names': r'\b(Landsat|Sentinel|MODIS|ASTER|SPOT|Pleiades|QuickBird|WorldView|IKONOS)\b',
            'resolution_patterns': r'(\d+(?:\.\d+)?)\s*(m|km|meters?|kilometers?)',
            'date_patterns': r'\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{4})\b',
            'coordinate_patterns': r'(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)',
            'band_patterns': r'\b(B\d+|Band\s+\d+|[RGB]|Red|Green|Blue|NIR|SWIR|TIR)\b'
        }
    
    def extract_dataset(self, soup: BeautifulSoup, url: str) -> DatasetMetadata:
        """Extract comprehensive dataset information"""
        # Basic extraction
        title = self._extract_title(soup)
        description = self._extract_description(soup)
        provider = self._extract_provider(soup)
        tags = self._extract_tags(soup)
        bands = self._extract_bands(soup)
        thumbnail_url = self._extract_thumbnail(soup)
        
        # AI-enhanced extraction
        text_content = soup.get_text()
        ml_classification = self.ai_classifier.classify_text(text_content)
        entities = self.ai_classifier.extract_entities(text_content)
        
        # Enhanced description
        enhanced_description = self.ai_classifier.generate_summary(description)
        
        # Spatial and temporal extraction
        spatial_coverage = self._extract_spatial_coverage(soup, entities)
        temporal_coverage = self._extract_temporal_coverage(soup, entities)
        
        # Resolution extraction
        resolution = self._extract_resolution(soup, text_content)
        
        # Create dataset metadata
        dataset = DatasetMetadata(
            id=self._generate_id(url, title),
            title=title,
            description=enhanced_description,
            provider=provider,
            tags=tags,
            spatial_coverage=spatial_coverage,
            temporal_coverage=temporal_coverage,
            bands=bands,
            resolution=resolution,
            thumbnail_url=thumbnail_url,
            source_url=url,
            citation=self._extract_citation(soup),
            terms_of_use=self._extract_terms_of_use(soup),
            data_type=ml_classification['final_classification']['category'],
            quality_score=0.0,  # Will be calculated by validator
            confidence_score=ml_classification['final_classification']['confidence'],
            extraction_timestamp=datetime.now(),
            ml_classification=ml_classification,
            validation_results={},
            enhanced_features={
                'entities': entities,
                'satellite_detected': self._detect_satellite(text_content),
                'resolution_detected': bool(resolution),
                'has_coordinates': bool(spatial_coverage.get('coordinates')),
                'has_dates': bool(temporal_coverage.get('start_date'))
            }
        )
        
        # Validate dataset
        dataset.validation_results = self.validator.validate_dataset(dataset)
        dataset.quality_score = dataset.validation_results['overall_score']
        
        return dataset
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract dataset title"""
        selectors = [
            'h1', 'h2', '.title', '.dataset-title', 
            'meta[property="og:title"]', 'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text().strip() if element.name != 'meta' else element.get('content', '')
                if title:
                    return title
        
        return "Untitled Dataset"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract dataset description"""
        selectors = [
            '.description', '.summary', '.abstract', 
            'meta[name="description"]', 'p'
        ]
        
        descriptions = []
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if len(text) > 20:  # Minimum meaningful length
                    descriptions.append(text)
        
        if descriptions:
            return ' '.join(descriptions[:3])  # Combine first 3 descriptions
        
        return "No description available"
    
    def _extract_provider(self, soup: BeautifulSoup) -> str:
        """Extract dataset provider"""
        selectors = [
            '.provider', '.source', '.organization',
            'meta[name="provider"]', 'a[href*="nasa"]', 'a[href*="esa"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                provider = element.get_text().strip()
                if provider:
                    return provider
        
        return "Unknown Provider"
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract dataset tags"""
        tags = []
        
        # Extract from tag elements
        tag_selectors = ['.tag', '.chip', '.label', 'span[class*="tag"]']
        for selector in tag_selectors:
            elements = soup.select(selector)
            for element in elements:
                tag = element.get_text().strip()
                if tag and len(tag) > 1:
                    tags.append(tag)
        
        # Extract from text content using patterns
        text = soup.get_text()
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            tags.extend(matches)
        
        return list(set(tags))  # Remove duplicates
    
    def _extract_bands(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract band information"""
        bands = []
        
        # Look for band tables
        band_tables = soup.select('table')
        for table in band_tables:
            rows = table.select('tr')
            for row in rows:
                cells = row.select('td')
                if len(cells) >= 2:
                    band_name = cells[0].get_text().strip()
                    band_description = cells[1].get_text().strip()
                    
                    if band_name and any(keyword in band_name.lower() for keyword in ['band', 'b', 'red', 'green', 'blue']):
                        bands.append({
                            'name': band_name,
                            'description': band_description,
                            'wavelength': self._extract_wavelength(band_description)
                        })
        
        return bands
    
    def _extract_wavelength(self, description: str) -> Optional[str]:
        """Extract wavelength information from band description"""
        wavelength_pattern = r'(\d+(?:\.\d+)?)\s*(nm|nanometers?|microns?)'
        match = re.search(wavelength_pattern, description, re.IGNORECASE)
        return match.group(0) if match else None
    
    def _extract_thumbnail(self, soup: BeautifulSoup) -> str:
        """Extract thumbnail URL"""
        selectors = [
            'img[src*="sample"]', 'img[src*="preview"]', 
            'img[src*="thumbnail"]', 'img[alt*="sample"]'
        ]
        
        for selector in selectors:
            img = soup.select_one(selector)
            if img and img.get('src'):
                return img['src']
        
        return ""
    
    def _extract_spatial_coverage(self, soup: BeautifulSoup, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Extract spatial coverage information"""
        coverage = {}
        
        # Extract from text using patterns
        text = soup.get_text()
        coordinates = re.findall(self.patterns['coordinate_patterns'], text)
        
        if coordinates:
            coverage['coordinates'] = [
                {'lat': float(lat), 'lon': float(lon)} 
                for lat, lon in coordinates[:4]  # Limit to 4 coordinates
            ]
        
        # Extract from entities
        if 'GPE' in entities:
            coverage['locations'] = entities['GPE']
        
        if 'LOC' in entities:
            coverage['locations'] = coverage.get('locations', []) + entities['LOC']
        
        return coverage
    
    def _extract_temporal_coverage(self, soup: BeautifulSoup, entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Extract temporal coverage information"""
        coverage = {}
        
        # Extract dates from text
        text = soup.get_text()
        dates = re.findall(self.patterns['date_patterns'], text)
        
        if dates:
            try:
                # Try to parse dates
                parsed_dates = []
                for date_str in dates:
                    try:
                        if '-' in date_str:
                            parsed_date = datetime.fromisoformat(date_str)
                        elif '/' in date_str:
                            parsed_date = datetime.strptime(date_str, '%m/%d/%Y')
                        else:
                            parsed_date = datetime(int(date_str), 1, 1)
                        parsed_dates.append(parsed_date)
                    except ValueError:
                        continue
                
                if parsed_dates:
                    parsed_dates.sort()
                    coverage['start_date'] = parsed_dates[0].isoformat()
                    coverage['end_date'] = parsed_dates[-1].isoformat()
                    
            except Exception as e:
                print(f"Date parsing failed: {e}")
        
        # Extract from entities
        if 'DATE' in entities:
            coverage['date_entities'] = entities['DATE']
        
        return coverage
    
    def _extract_resolution(self, soup: BeautifulSoup, text: str) -> Dict[str, Any]:
        """Extract resolution information"""
        resolution = {}
        
        # Find resolution patterns
        matches = re.findall(self.patterns['resolution_patterns'], text, re.IGNORECASE)
        
        if matches:
            resolutions = []
            for value, unit in matches:
                try:
                    value = float(value)
                    if unit.lower() in ['km', 'kilometers']:
                        value *= 1000  # Convert to meters
                    resolutions.append({'value': value, 'unit': 'meters'})
                except ValueError:
                    continue
            
            if resolutions:
                # Get the most common resolution
                resolution['values'] = resolutions
                resolution['primary'] = min(resolutions, key=lambda x: x['value'])
        
        return resolution
    
    def _extract_citation(self, soup: BeautifulSoup) -> str:
        """Extract citation information"""
        selectors = ['.citation', '.cite', 'div[class*="citation"]']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return ""
    
    def _extract_terms_of_use(self, soup: BeautifulSoup) -> str:
        """Extract terms of use information"""
        selectors = ['.terms', '.license', 'div[class*="terms"]']
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return ""
    
    def _generate_id(self, url: str, title: str) -> str:
        """Generate unique dataset ID"""
        content = f"{url}_{title}".encode('utf-8')
        return hashlib.md5(content).hexdigest()[:12]
    
    def _detect_satellite(self, text: str) -> bool:
        """Detect if satellite data is mentioned"""
        satellite_pattern = self.patterns['satellite_names']
        return bool(re.search(satellite_pattern, text, re.IGNORECASE))

class EnhancedCrawlerV5:
    """Enhanced web crawler with advanced AI capabilities"""
    
    def __init__(self, config_path: str = "crawler_config_v5.yaml"):
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.ai_classifier = AdvancedAIClassifier(
            cache_dir=self.config.get('ai_cache_dir', 'ai_cache')
        )
        self.validator = AdvancedDataValidator()
        self.extractor = AdvancedDataExtractor(self.ai_classifier, self.validator)
        
        # Performance tracking
        self.stats = {
            'datasets_processed': 0,
            'datasets_extracted': 0,
            'errors': 0,
            'start_time': None,
            'processing_rate': 0.0
        }
        
        # Setup logging
        self._setup_logging()
        
        # Initialize webdriver
        self.driver = None
        self._setup_webdriver()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration file"""
        default_config = {
            'ai_cache_dir': 'ai_cache',
            'output_dir': 'extracted_data_v5',
            'max_concurrent_requests': 5,
            'request_delay': 1.0,
            'timeout': 30,
            'max_retries': 3,
            'enable_ai': True,
            'enable_validation': True,
            'enable_async': True,
            'log_level': 'INFO'
        }
        
        if YAML_AVAILABLE and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    return {**default_config, **config}
            except Exception as e:
                print(f"Failed to load config: {e}")
        
        return default_config
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config.get('log_level', 'INFO'))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler_v5.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _setup_webdriver(self):
        """Setup Selenium webdriver"""
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Edge(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
        except Exception as e:
            self.logger.error(f"Failed to setup webdriver: {e}")
            self.driver = None
    
    def crawl_html_file(self, html_file: str, output_file: str = None) -> List[DatasetMetadata]:
        """Crawl HTML file and extract datasets"""
        self.stats['start_time'] = datetime.now()
        self.logger.info(f"Starting crawl of {html_file}")
        
        try:
            # Read HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find dataset links
            dataset_links = self._find_dataset_links(soup)
            self.logger.info(f"Found {len(dataset_links)} dataset links")
            
            # Extract datasets
            datasets = []
            for i, link in enumerate(dataset_links):
                try:
                    self.logger.info(f"Processing dataset {i+1}/{len(dataset_links)}: {link}")
                    
                    dataset = self._extract_single_dataset(link)
                    if dataset:
                        datasets.append(dataset)
                        self.stats['datasets_extracted'] += 1
                    
                    # Rate limiting
                    time.sleep(self.config.get('request_delay', 1.0))
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {link}: {e}")
                    self.stats['errors'] += 1
                
                self.stats['datasets_processed'] += 1
            
            # Save results
            if output_file:
                self._save_results(datasets, output_file)
            
            # Log final stats
            self._log_final_stats()
            
            return datasets
            
        except Exception as e:
            self.logger.error(f"Crawl failed: {e}")
            return []
    
    def _find_dataset_links(self, soup: BeautifulSoup) -> List[str]:
        """Find dataset links in HTML"""
        links = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and ('catalog' in href or 'datasets' in href):
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    href = f"https://developers.google.com{href}"
                elif not href.startswith('http'):
                    href = urljoin("https://developers.google.com/earth-engine/datasets/", href)
                
                links.append(href)
        
        # Remove duplicates and return
        return list(set(links))
    
    def _extract_single_dataset(self, url: str) -> Optional[DatasetMetadata]:
        """Extract single dataset from URL"""
        try:
            # Use Selenium for dynamic content
            if self.driver:
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                html_content = self.driver.page_source
            else:
                # Fallback to requests
                response = requests.get(url, timeout=self.config.get('timeout', 30))
                response.raise_for_status()
                html_content = response.text
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract dataset using AI-enhanced extractor
            dataset = self.extractor.extract_dataset(soup, url)
            
            return dataset
            
        except Exception as e:
            self.logger.error(f"Failed to extract dataset from {url}: {e}")
            return None
    
    def _save_results(self, datasets: List[DatasetMetadata], output_file: str):
        """Save results to file"""
        try:
            # Convert datasets to dictionaries
            data = {
                'metadata': {
                    'crawl_timestamp': datetime.now().isoformat(),
                    'total_datasets': len(datasets),
                    'crawler_version': '5.0',
                    'config': self.config
                },
                'datasets': [asdict(dataset) for dataset in datasets]
            }
            
            # Save as JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Save compressed version
            compressed_file = output_file.replace('.json', '.json.gz')
            with gzip.open(compressed_file, 'wt', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to {output_file} and {compressed_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
    
    def _log_final_stats(self):
        """Log final crawling statistics"""
        if self.stats['start_time']:
            duration = datetime.now() - self.stats['start_time']
            self.stats['processing_rate'] = self.stats['datasets_processed'] / duration.total_seconds()
        
        self.logger.info("Crawling completed!")
        self.logger.info(f"Datasets processed: {self.stats['datasets_processed']}")
        self.logger.info(f"Datasets extracted: {self.stats['datasets_extracted']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info(f"Processing rate: {self.stats['processing_rate']:.2f} datasets/second")
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Earth Engine Web Crawler v5.0')
    parser.add_argument('html_file', help='HTML file to crawl')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-c', '--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize crawler
    crawler = EnhancedCrawlerV5(config_path=args.config)
    
    try:
        # Run crawl
        output_file = args.output or f"crawler_results_v5_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        datasets = crawler.crawl_html_file(args.html_file, output_file)
        
        print(f"Crawling completed! Extracted {len(datasets)} datasets.")
        print(f"Results saved to: {output_file}")
        
    finally:
        crawler.close()

if __name__ == "__main__":
    main() 