#!/usr/bin/env python3
"""
Adaptive Data Weight Optimizer for Enhanced Web Crawler
Tests different data weights during crawling to find optimal configurations
"""

import time
import json
import gc
import psutil
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging
import pickle
import os
from pathlib import Path

@dataclass
class WeightConfiguration:
    """Configuration for data weight testing"""
    name: str
    title_weight: float
    description_weight: float
    tags_weight: float
    technical_weight: float
    spatial_weight: float
    temporal_weight: float
    quality_threshold: float
    confidence_threshold: float
    max_tokens: int
    timeout_seconds: int
    memory_limit_mb: int

@dataclass
class WeightTestResult:
    """Result of a weight configuration test"""
    config_name: str
    total_items: int
    successful_extractions: int
    average_quality: float
    average_confidence: float
    processing_time: float
    memory_usage: float
    error_rate: float
    unique_categories: int
    data_completeness: float
    technical_accuracy: float
    spatial_accuracy: float
    temporal_accuracy: float

class AdaptiveDataWeightOptimizer:
    """Adaptive system for testing and optimizing data weights during crawling"""
    
    def __init__(self, cache_dir: str = "weight_optimization_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Load or create default configurations
        self.weight_configs = self._load_default_configurations()
        self.test_results = []
        self.current_best_config = None
        self.optimization_history = []
        
        # Performance tracking
        self.performance_metrics = defaultdict(list)
        self.memory_tracker = []
        
        # BERT fallback system
        self.bert_available = False
        self.fallback_classifier = None
        self._setup_bert_fallback()
    
    def _load_default_configurations(self) -> List[WeightConfiguration]:
        """Load default weight configurations for testing"""
        configs = [
            # Balanced configuration
            WeightConfiguration(
                name="balanced",
                title_weight=0.3,
                description_weight=0.4,
                tags_weight=0.2,
                technical_weight=0.3,
                spatial_weight=0.25,
                temporal_weight=0.25,
                quality_threshold=0.6,
                confidence_threshold=0.7,
                max_tokens=256,
                timeout_seconds=5,
                memory_limit_mb=512
            ),
            # Title-focused configuration
            WeightConfiguration(
                name="title_focused",
                title_weight=0.5,
                description_weight=0.3,
                tags_weight=0.2,
                technical_weight=0.4,
                spatial_weight=0.3,
                temporal_weight=0.2,
                quality_threshold=0.7,
                confidence_threshold=0.8,
                max_tokens=128,
                timeout_seconds=3,
                memory_limit_mb=256
            ),
            # Description-focused configuration
            WeightConfiguration(
                name="description_focused",
                title_weight=0.2,
                description_weight=0.6,
                tags_weight=0.2,
                technical_weight=0.25,
                spatial_weight=0.25,
                temporal_weight=0.3,
                quality_threshold=0.5,
                confidence_threshold=0.6,
                max_tokens=512,
                timeout_seconds=8,
                memory_limit_mb=1024
            ),
            # Technical-focused configuration
            WeightConfiguration(
                name="technical_focused",
                title_weight=0.25,
                description_weight=0.35,
                tags_weight=0.4,
                technical_weight=0.5,
                spatial_weight=0.2,
                temporal_weight=0.2,
                quality_threshold=0.8,
                confidence_threshold=0.9,
                max_tokens=384,
                timeout_seconds=6,
                memory_limit_mb=768
            ),
            # Memory-efficient configuration
            WeightConfiguration(
                name="memory_efficient",
                title_weight=0.4,
                description_weight=0.4,
                tags_weight=0.2,
                technical_weight=0.2,
                spatial_weight=0.2,
                temporal_weight=0.2,
                quality_threshold=0.4,
                confidence_threshold=0.5,
                max_tokens=128,
                timeout_seconds=3,
                memory_limit_mb=256
            )
        ]
        
        # Save configurations
        self._save_configurations(configs)
        return configs
    
    def _setup_bert_fallback(self):
        """Setup BERT with comprehensive fallback system"""
        try:
            # Try to load transformers
            import transformers
            from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
            
            # Test with lightweight model
            self.logger.info("Testing BERT model loading...")
            
            # Create a simple test classifier
            tokenizer = AutoTokenizer.from_pretrained(
                "distilbert-base-uncased",
                trust_remote_code=True,
                use_auth_token=False
            )
            
            model = AutoModelForSequenceClassification.from_pretrained(
                "distilbert-base-uncased",
                num_labels=5,
                trust_remote_code=True,
                use_auth_token=False
            )
            
            self.bert_classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=-1,  # CPU
                return_all_scores=False
            )
            
            # Test the classifier
            test_result = self.bert_classifier("test sentence", truncation=True, max_length=128)
            if test_result:
                self.bert_available = True
                self.logger.info("✅ BERT model loaded successfully")
            else:
                raise Exception("BERT test failed")
                
        except Exception as e:
            self.logger.warning(f"BERT loading failed: {e}")
            self.bert_available = False
            self._create_fallback_classifier()
    
    def _create_fallback_classifier(self):
        """Create a comprehensive fallback classifier"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.pipeline import Pipeline
            
            # Create enhanced fallback classifier
            self.fallback_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=500,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.9
                )),
                ('classifier', MultinomialNB())
            ])
            
            # Train on comprehensive dataset
            training_texts = [
                "satellite imagery", "remote sensing", "earth observation", "landsat", "sentinel",
                "climate data", "weather data", "atmospheric science", "environmental monitoring",
                "geospatial data", "geographic information", "coordinate system", "spatial analysis",
                "temporal data", "time series", "historical data", "temporal analysis",
                "technical specifications", "sensor data", "resolution", "spectral bands",
                "optical data", "radar data", "infrared", "multispectral", "hyperspectral",
                "disaster monitoring", "emergency response", "flood mapping", "fire detection",
                "agriculture", "crop monitoring", "vegetation index", "land use",
                "urban development", "infrastructure", "transportation", "population density",
                "oceanography", "marine data", "coastal monitoring", "water resources",
                "geology", "mineral exploration", "seismic data", "geological mapping"
            ]
            
            training_labels = [
                "satellite_data", "satellite_data", "satellite_data", "satellite_data", "satellite_data",
                "climate_data", "climate_data", "climate_data", "climate_data",
                "geospatial_data", "geospatial_data", "geospatial_data", "geospatial_data",
                "temporal_data", "temporal_data", "temporal_data", "temporal_data",
                "technical_data", "technical_data", "technical_data", "technical_data",
                "optical_data", "radar_data", "optical_data", "optical_data", "optical_data",
                "disaster_data", "disaster_data", "disaster_data", "disaster_data",
                "agricultural_data", "agricultural_data", "agricultural_data", "agricultural_data",
                "urban_data", "urban_data", "urban_data", "urban_data",
                "oceanographic_data", "oceanographic_data", "oceanographic_data", "oceanographic_data",
                "geological_data", "geological_data", "geological_data", "geological_data"
            ]
            
            self.fallback_classifier.fit(training_texts, training_labels)
            self.logger.info("✅ Fallback classifier created successfully")
            
        except Exception as e:
            self.logger.error(f"Fallback classifier creation failed: {e}")
            self.fallback_classifier = None
    
    def classify_text(self, text: str, config: WeightConfiguration) -> Dict[str, Any]:
        """Classify text using current configuration"""
        if not text:
            return {'label': 'unknown', 'confidence': 0.0, 'method': 'empty_text'}
        
        try:
            if self.bert_available and config.max_tokens > 0:
                # Use BERT with configuration limits
                result = self.bert_classifier(
                    text,
                    truncation=True,
                    max_length=config.max_tokens,
                    padding=True,
                    return_all_scores=False
                )
                
                if result and len(result) > 0:
                    return {
                        'label': result[0]['label'],
                        'confidence': result[0]['score'],
                        'method': 'bert'
                    }
            
            # Fallback to TF-IDF classifier
            if self.fallback_classifier:
                prediction = self.fallback_classifier.predict([text])[0]
                confidence = max(self.fallback_classifier.predict_proba([text])[0])
                
                return {
                    'label': prediction,
                    'confidence': confidence,
                    'method': 'fallback_tfidf'
                }
            
            # Final fallback to keyword matching
            return self._keyword_classify(text)
            
        except Exception as e:
            self.logger.warning(f"Classification failed: {e}")
            return self._keyword_classify(text)
    
    def _keyword_classify(self, text: str) -> Dict[str, Any]:
        """Simple keyword-based classification as final fallback"""
        text_lower = text.lower()
        
        keywords = {
            'satellite_data': ['satellite', 'sensor', 'radar', 'optical', 'resolution', 'landsat', 'sentinel'],
            'climate_data': ['climate', 'weather', 'atmosphere', 'temperature', 'precipitation'],
            'geospatial_data': ['geographic', 'coordinate', 'latitude', 'longitude', 'spatial'],
            'temporal_data': ['temporal', 'time', 'historical', 'time series', 'temporal'],
            'technical_data': ['technical', 'specification', 'parameter', 'metadata'],
            'disaster_data': ['disaster', 'emergency', 'flood', 'fire', 'earthquake'],
            'agricultural_data': ['agriculture', 'crop', 'vegetation', 'farming'],
            'urban_data': ['urban', 'city', 'infrastructure', 'population'],
            'oceanographic_data': ['ocean', 'marine', 'coastal', 'water'],
            'geological_data': ['geology', 'mineral', 'seismic', 'geological']
        }
        
        scores = {}
        for category, category_keywords in keywords.items():
            score = sum(1 for keyword in category_keywords if keyword in text_lower)
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            confidence = min(scores[best_category] / 5.0, 1.0)
            return {
                'label': best_category,
                'confidence': confidence,
                'method': 'keyword'
            }
        else:
            return {
                'label': 'general_data',
                'confidence': 0.3,
                'method': 'keyword'
            }
    
    def test_configuration(self, config: WeightConfiguration, test_data: List[Dict[str, Any]]) -> WeightTestResult:
        """Test a specific weight configuration"""
        self.logger.info(f"Testing configuration: {config.name}")
        
        start_time = time.time()
        start_memory = psutil.virtual_memory().percent
        
        successful_extractions = 0
        total_quality = 0.0
        total_confidence = 0.0
        errors = 0
        categories = set()
        
        for item in test_data:
            try:
                # Apply configuration weights
                weighted_text = self._apply_weights(item, config)
                
                # Classify with current configuration
                classification = self.classify_text(weighted_text, config)
                
                if classification['confidence'] >= config.confidence_threshold:
                    successful_extractions += 1
                    total_confidence += classification['confidence']
                    categories.add(classification['label'])
                
                # Calculate quality score
                quality = self._calculate_quality_score(item, classification, config)
                total_quality += quality
                
            except Exception as e:
                errors += 1
                self.logger.warning(f"Error processing item: {e}")
        
        end_time = time.time()
        end_memory = psutil.virtual_memory().percent
        
        processing_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        # Calculate metrics
        total_items = len(test_data)
        average_quality = total_quality / total_items if total_items > 0 else 0.0
        average_confidence = total_confidence / successful_extractions if successful_extractions > 0 else 0.0
        error_rate = errors / total_items if total_items > 0 else 0.0
        unique_categories = len(categories)
        data_completeness = successful_extractions / total_items if total_items > 0 else 0.0
        
        # Calculate accuracy metrics
        technical_accuracy = self._calculate_technical_accuracy(test_data, config)
        spatial_accuracy = self._calculate_spatial_accuracy(test_data, config)
        temporal_accuracy = self._calculate_temporal_accuracy(test_data, config)
        
        result = WeightTestResult(
            config_name=config.name,
            total_items=total_items,
            successful_extractions=successful_extractions,
            average_quality=average_quality,
            average_confidence=average_confidence,
            processing_time=processing_time,
            memory_usage=memory_usage,
            error_rate=error_rate,
            unique_categories=unique_categories,
            data_completeness=data_completeness,
            technical_accuracy=technical_accuracy,
            spatial_accuracy=spatial_accuracy,
            temporal_accuracy=temporal_accuracy
        )
        
        self.test_results.append(result)
        self._save_test_result(result)
        
        self.logger.info(f"Configuration {config.name} test completed:")
        self.logger.info(f"  - Success rate: {data_completeness:.2%}")
        self.logger.info(f"  - Average quality: {average_quality:.2f}")
        self.logger.info(f"  - Processing time: {processing_time:.2f}s")
        self.logger.info(f"  - Memory usage: {memory_usage:.1f}%")
        
        return result
    
    def _apply_weights(self, item: Dict[str, Any], config: WeightConfiguration) -> str:
        """Apply weight configuration to item text"""
        title = item.get('title', '') or ''
        description = item.get('description', '') or ''
        tags = item.get('tags', '') or ''
        
        # Apply weights
        weighted_text = (
            f"{title} " * int(config.title_weight * 10) +
            f"{description} " * int(config.description_weight * 10) +
            f"{tags} " * int(config.tags_weight * 10)
        )
        
        return weighted_text.strip()
    
    def _calculate_quality_score(self, item: Dict[str, Any], classification: Dict[str, Any], config: WeightConfiguration) -> float:
        """Calculate quality score for an item"""
        quality = 0.0
        
        # Base quality from confidence
        quality += classification['confidence'] * 0.4
        
        # Content completeness
        title = item.get('title', '')
        description = item.get('description', '')
        tags = item.get('tags', '')
        
        content_length = len(title) + len(description) + len(tags)
        if content_length > 100:
            quality += 0.2
        elif content_length > 50:
            quality += 0.1
        
        # Technical content
        technical_terms = ['satellite', 'sensor', 'resolution', 'spectral', 'radar', 'optical']
        technical_count = sum(1 for term in technical_terms if term.lower() in (title + description).lower())
        quality += min(technical_count * 0.1, 0.3)
        
        # Spatial content
        spatial_terms = ['latitude', 'longitude', 'coordinate', 'geographic', 'spatial']
        spatial_count = sum(1 for term in spatial_terms if term.lower() in (title + description).lower())
        quality += min(spatial_count * 0.1, 0.2)
        
        # Temporal content
        temporal_terms = ['time', 'temporal', 'historical', 'date', 'period']
        temporal_count = sum(1 for term in temporal_terms if term.lower() in (title + description).lower())
        quality += min(temporal_count * 0.1, 0.2)
        
        return min(quality, 1.0)
    
    def _calculate_technical_accuracy(self, test_data: List[Dict[str, Any]], config: WeightConfiguration) -> float:
        """Calculate technical accuracy"""
        technical_items = 0
        correct_technical = 0
        
        for item in test_data:
            text = self._apply_weights(item, config)
            if any(term in text.lower() for term in ['satellite', 'sensor', 'resolution', 'spectral']):
                technical_items += 1
                classification = self.classify_text(text, config)
                if 'satellite' in classification['label'] or 'technical' in classification['label']:
                    correct_technical += 1
        
        return correct_technical / technical_items if technical_items > 0 else 0.0
    
    def _calculate_spatial_accuracy(self, test_data: List[Dict[str, Any]], config: WeightConfiguration) -> float:
        """Calculate spatial accuracy"""
        spatial_items = 0
        correct_spatial = 0
        
        for item in test_data:
            text = self._apply_weights(item, config)
            if any(term in text.lower() for term in ['latitude', 'longitude', 'coordinate', 'geographic']):
                spatial_items += 1
                classification = self.classify_text(text, config)
                if 'geospatial' in classification['label'] or 'spatial' in classification['label']:
                    correct_spatial += 1
        
        return correct_spatial / spatial_items if spatial_items > 0 else 0.0
    
    def _calculate_temporal_accuracy(self, test_data: List[Dict[str, Any]], config: WeightConfiguration) -> float:
        """Calculate temporal accuracy"""
        temporal_items = 0
        correct_temporal = 0
        
        for item in test_data:
            text = self._apply_weights(item, config)
            if any(term in text.lower() for term in ['time', 'temporal', 'historical', 'date']):
                temporal_items += 1
                classification = self.classify_text(text, config)
                if 'temporal' in classification['label'] or 'time' in classification['label']:
                    correct_temporal += 1
        
        return correct_temporal / temporal_items if temporal_items > 0 else 0.0
    
    def find_optimal_configuration(self, test_data: List[Dict[str, Any]]) -> WeightConfiguration:
        """Find the optimal configuration based on test results"""
        self.logger.info("Finding optimal configuration...")
        
        # Test all configurations
        for config in self.weight_configs:
            self.test_configuration(config, test_data)
        
        # Find best configuration based on composite score
        best_config = None
        best_score = 0.0
        
        for result in self.test_results:
            # Composite score calculation
            score = (
                result.average_quality * 0.3 +
                result.average_confidence * 0.2 +
                result.data_completeness * 0.2 +
                result.technical_accuracy * 0.1 +
                result.spatial_accuracy * 0.1 +
                result.temporal_accuracy * 0.1 -
                result.error_rate * 0.2 -
                (result.processing_time / 100) * 0.1 -
                (result.memory_usage / 100) * 0.1
            )
            
            if score > best_score:
                best_score = score
                best_config = next(c for c in self.weight_configs if c.name == result.config_name)
        
        if best_config:
            self.current_best_config = best_config
            self.logger.info(f"Optimal configuration found: {best_config.name}")
            self.logger.info(f"Composite score: {best_score:.3f}")
        
        return best_config
    
    def adaptive_optimization(self, test_data: List[Dict[str, Any]], max_iterations: int = 3) -> WeightConfiguration:
        """Perform adaptive optimization with multiple iterations"""
        self.logger.info("Starting adaptive optimization...")
        
        current_config = self.weight_configs[0]  # Start with balanced config
        
        for iteration in range(max_iterations):
            self.logger.info(f"Optimization iteration {iteration + 1}/{max_iterations}")
            
            # Test current configuration
            result = self.test_configuration(current_config, test_data)
            
            # Analyze results and adjust configuration
            adjusted_config = self._adjust_configuration(current_config, result)
            
            if adjusted_config:
                current_config = adjusted_config
                self.logger.info(f"Configuration adjusted: {current_config.name}")
            else:
                self.logger.info("No further adjustments needed")
                break
        
        self.current_best_config = current_config
        return current_config
    
    def _adjust_configuration(self, config: WeightConfiguration, result: WeightTestResult) -> Optional[WeightConfiguration]:
        """Adjust configuration based on test results"""
        adjustments = []
        
        # Adjust based on quality
        if result.average_quality < 0.6:
            adjustments.append(('quality_threshold', config.quality_threshold * 0.9))
        
        # Adjust based on confidence
        if result.average_confidence < 0.7:
            adjustments.append(('confidence_threshold', config.confidence_threshold * 0.9))
        
        # Adjust based on processing time
        if result.processing_time > 10:
            adjustments.append(('max_tokens', max(64, config.max_tokens - 64)))
            adjustments.append(('timeout_seconds', max(2, config.timeout_seconds - 1)))
        
        # Adjust based on memory usage
        if result.memory_usage > 5:
            adjustments.append(('memory_limit_mb', max(256, config.memory_limit_mb - 128)))
        
        # Adjust weights based on accuracy
        if result.technical_accuracy < 0.7:
            adjustments.append(('technical_weight', min(0.8, config.technical_weight * 1.1)))
        
        if result.spatial_accuracy < 0.7:
            adjustments.append(('spatial_weight', min(0.8, config.spatial_weight * 1.1)))
        
        if result.temporal_accuracy < 0.7:
            adjustments.append(('temporal_weight', min(0.8, config.temporal_weight * 1.1)))
        
        if adjustments:
            # Create new configuration with adjustments
            new_config = WeightConfiguration(
                name=f"{config.name}_optimized_{len(self.optimization_history)}",
                title_weight=config.title_weight,
                description_weight=config.description_weight,
                tags_weight=config.tags_weight,
                technical_weight=config.technical_weight,
                spatial_weight=config.spatial_weight,
                temporal_weight=config.temporal_weight,
                quality_threshold=config.quality_threshold,
                confidence_threshold=config.confidence_threshold,
                max_tokens=config.max_tokens,
                timeout_seconds=config.timeout_seconds,
                memory_limit_mb=config.memory_limit_mb
            )
            
            # Apply adjustments
            for attr, value in adjustments:
                setattr(new_config, attr, value)
            
            self.optimization_history.append(new_config)
            return new_config
        
        return None
    
    def _save_configurations(self, configs: List[WeightConfiguration]):
        """Save configurations to file"""
        config_file = self.cache_dir / "weight_configurations.json"
        config_data = [asdict(config) for config in configs]
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def _save_test_result(self, result: WeightTestResult):
        """Save test result to file"""
        result_file = self.cache_dir / f"test_result_{result.config_name}.json"
        
        with open(result_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate optimization report"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        report = {
            "total_configurations_tested": len(self.test_results),
            "best_configuration": self.current_best_config.name if self.current_best_config else None,
            "optimization_iterations": len(self.optimization_history),
            "test_results": [asdict(result) for result in self.test_results],
            "system_info": {
                "bert_available": self.bert_available,
                "fallback_classifier_available": self.fallback_classifier is not None,
                "memory_usage": psutil.virtual_memory().percent,
                "cache_directory": str(self.cache_dir)
            }
        }
        
        return report
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Clear BERT model from memory
            if hasattr(self, 'bert_classifier'):
                del self.bert_classifier
            
            # Clear fallback classifier
            if self.fallback_classifier:
                del self.fallback_classifier
            
            # Force garbage collection
            gc.collect()
            
            self.logger.info("Cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Cleanup error: {e}")

def create_adaptive_optimizer() -> AdaptiveDataWeightOptimizer:
    """Create and return an adaptive data weight optimizer"""
    return AdaptiveDataWeightOptimizer()

if __name__ == "__main__":
    # Test the optimizer
    optimizer = create_adaptive_optimizer()
    
    # Create sample test data
    test_data = [
        {"title": "Landsat 8 Satellite Imagery", "description": "High-resolution optical satellite data", "tags": "satellite, optical, remote sensing"},
        {"title": "Climate Data Collection", "description": "Atmospheric temperature and precipitation data", "tags": "climate, weather, atmosphere"},
        {"title": "Geographic Coordinate System", "description": "Spatial reference system for mapping", "tags": "geospatial, coordinate, mapping"},
        {"title": "Historical Time Series Data", "description": "Temporal analysis of environmental changes", "tags": "temporal, historical, time series"},
        {"title": "Technical Sensor Specifications", "description": "Detailed sensor parameters and metadata", "tags": "technical, sensor, specification"}
    ]
    
    # Find optimal configuration
    optimal_config = optimizer.find_optimal_configuration(test_data)
    
    if optimal_config:
        print(f"✅ Optimal configuration found: {optimal_config.name}")
        print(f"📊 Configuration details:")
        print(f"   - Title weight: {optimal_config.title_weight}")
        print(f"   - Description weight: {optimal_config.description_weight}")
        print(f"   - Quality threshold: {optimal_config.quality_threshold}")
        print(f"   - Max tokens: {optimal_config.max_tokens}")
    
    # Generate report
    report = optimizer.get_optimization_report()
    print(f"\n📈 Optimization Report:")
    print(f"   - Configurations tested: {report['total_configurations_tested']}")
    print(f"   - BERT available: {report['system_info']['bert_available']}")
    print(f"   - Memory usage: {report['system_info']['memory_usage']:.1f}%")
    
    optimizer.cleanup() 