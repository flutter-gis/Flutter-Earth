#!/usr/bin/env python3
"""
BERT Fix and Adaptive Weight Optimizer for Enhanced Web Crawler
Fixes BERT training data errors and implements adaptive weight testing during crawling
"""

import sys
import time
import gc
import psutil
import logging
import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WeightTestConfig:
    """Configuration for weight testing during crawling"""
    name: str
    title_weight: float = 0.3
    description_weight: float = 0.4
    tags_weight: float = 0.2
    technical_weight: float = 0.3
    spatial_weight: float = 0.25
    temporal_weight: float = 0.25
    quality_threshold: float = 0.6
    confidence_threshold: float = 0.7
    max_tokens: int = 256
    timeout_seconds: int = 5
    memory_limit_mb: int = 512

class BERTFixAndWeightOptimizer:
    """Comprehensive BERT fix and adaptive weight optimization system"""
    
    def __init__(self):
        self.bert_available = False
        self.fallback_classifier = None
        self.weight_configs = []
        self.test_results = []
        self.current_best_config = None
        self.optimization_cache = Path("weight_optimization_cache")
        self.optimization_cache.mkdir(exist_ok=True)
        
        # Initialize systems
        self._fix_bert_issues()
        self._setup_weight_configurations()
        self._create_fallback_systems()
    
    def _fix_bert_issues(self):
        """Fix BERT training data and loading issues"""
        logger.info("🔧 Fixing BERT issues...")
        
        try:
            # Try to import transformers with error handling
            import transformers
            from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
            
            logger.info("✅ Transformers imported successfully")
            
            # Test with lightweight model first
            try:
                logger.info("📥 Testing with distilbert-base-uncased...")
                
                tokenizer = AutoTokenizer.from_pretrained(
                    "distilbert-base-uncased",
                    trust_remote_code=True,
                    use_auth_token=False,
                    revision="main",
                    local_files_only=False
                )
                logger.info("✅ Tokenizer loaded successfully")
                
                model = AutoModelForSequenceClassification.from_pretrained(
                    "distilbert-base-uncased",
                    num_labels=5,
                    trust_remote_code=True,
                    use_auth_token=False,
                    revision="main",
                    local_files_only=False
                )
                logger.info("✅ Model loaded successfully")
                
                # Create pipeline with memory optimization
                self.bert_classifier = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1,  # Force CPU for memory efficiency
                    return_all_scores=False
                )
                
                # Test the classifier
                test_result = self.bert_classifier(
                    "This is a test sentence for BERT classification",
                    truncation=True,
                    max_length=128
                )
                
                if test_result and len(test_result) > 0:
                    self.bert_available = True
                    logger.info("🎉 BERT model working successfully!")
                    logger.info(f"Test result: {test_result}")
                else:
                    raise Exception("BERT test returned empty result")
                    
            except Exception as e:
                logger.warning(f"DistilBERT failed: {e}")
                self._try_alternative_bert_models()
                
        except Exception as e:
            logger.error(f"Transformers import failed: {e}")
            self._create_comprehensive_fallback()
    
    def _try_alternative_bert_models(self):
        """Try alternative BERT models if primary fails"""
        alternative_models = [
            "bert-base-uncased",
            "microsoft/DialoGPT-small",
            "facebook/bart-base"
        ]
        
        for model_name in alternative_models:
            try:
                logger.info(f"🔄 Trying alternative model: {model_name}")
                
                from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
                
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    use_auth_token=False
                )
                
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    num_labels=5,
                    trust_remote_code=True,
                    use_auth_token=False
                )
                
                self.bert_classifier = pipeline(
                    "text-classification",
                    model=model,
                    tokenizer=tokenizer,
                    device=-1
                )
                
                # Test
                test_result = self.bert_classifier("test sentence", truncation=True, max_length=128)
                if test_result:
                    self.bert_available = True
                    logger.info(f"✅ Alternative model {model_name} working!")
                    return
                    
            except Exception as e:
                logger.warning(f"Alternative model {model_name} failed: {e}")
                continue
        
        logger.warning("All BERT models failed, using comprehensive fallback")
        self._create_comprehensive_fallback()
    
    def _create_comprehensive_fallback(self):
        """Create comprehensive fallback classification system"""
        logger.info("🛠️ Creating comprehensive fallback system...")
        
        try:
            # Create enhanced TF-IDF classifier
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.naive_bayes import MultinomialNB
            from sklearn.pipeline import Pipeline
            
            self.fallback_classifier = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.9
                )),
                ('classifier', MultinomialNB())
            ])
            
            # Comprehensive training data
            training_data = {
                'satellite_data': [
                    "satellite imagery", "remote sensing", "earth observation", "landsat", "sentinel",
                    "optical sensor", "radar data", "multispectral", "hyperspectral", "resolution",
                    "sensor specifications", "spectral bands", "satellite data", "spaceborne"
                ],
                'climate_data': [
                    "climate data", "weather data", "atmospheric science", "environmental monitoring",
                    "temperature data", "precipitation data", "climate change", "weather monitoring",
                    "atmospheric conditions", "climate analysis", "weather patterns"
                ],
                'geospatial_data': [
                    "geospatial data", "geographic information", "coordinate system", "spatial analysis",
                    "mapping data", "geographic coordinates", "spatial reference", "geographic data",
                    "coordinate transformation", "spatial indexing", "geographic mapping"
                ],
                'temporal_data': [
                    "temporal data", "time series", "historical data", "temporal analysis",
                    "time-based data", "historical records", "temporal patterns", "time sequence",
                    "chronological data", "temporal trends", "time-based analysis"
                ],
                'technical_data': [
                    "technical specifications", "sensor data", "metadata", "technical parameters",
                    "data quality", "technical documentation", "specification data", "technical details",
                    "parameter data", "technical analysis", "specification information"
                ],
                'disaster_data': [
                    "disaster monitoring", "emergency response", "flood mapping", "fire detection",
                    "disaster data", "emergency data", "hazard monitoring", "disaster analysis",
                    "emergency mapping", "disaster assessment", "hazard data"
                ],
                'agricultural_data': [
                    "agriculture data", "crop monitoring", "vegetation index", "land use",
                    "agricultural monitoring", "crop data", "vegetation data", "agricultural analysis",
                    "land use data", "crop assessment", "agricultural mapping"
                ],
                'urban_data': [
                    "urban development", "infrastructure", "transportation", "population density",
                    "urban data", "city data", "infrastructure data", "urban analysis",
                    "population data", "urban mapping", "city planning data"
                ],
                'oceanographic_data': [
                    "oceanography", "marine data", "coastal monitoring", "water resources",
                    "oceanographic data", "marine science", "coastal data", "ocean data",
                    "marine monitoring", "coastal analysis", "oceanographic analysis"
                ],
                'geological_data': [
                    "geology", "mineral exploration", "seismic data", "geological mapping",
                    "geological data", "mineral data", "seismic analysis", "geological analysis",
                    "mineral exploration data", "geological monitoring", "seismic monitoring"
                ]
            }
            
            # Prepare training data
            texts = []
            labels = []
            
            for category, category_texts in training_data.items():
                texts.extend(category_texts)
                labels.extend([category] * len(category_texts))
            
            # Train the classifier
            self.fallback_classifier.fit(texts, labels)
            
            # Test the classifier
            test_text = "NASA Landsat 8 satellite imagery with high resolution"
            prediction = self.fallback_classifier.predict([test_text])[0]
            confidence = max(self.fallback_classifier.predict_proba([test_text])[0])
            
            logger.info(f"✅ Fallback classifier created successfully")
            logger.info(f"Test prediction: {prediction} (confidence: {confidence:.3f})")
            
        except Exception as e:
            logger.error(f"Fallback classifier creation failed: {e}")
            self.fallback_classifier = None
    
    def _setup_weight_configurations(self):
        """Setup weight configurations for testing"""
        logger.info("⚙️ Setting up weight configurations...")
        
        self.weight_configs = [
            WeightTestConfig(
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
            WeightTestConfig(
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
            WeightTestConfig(
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
            WeightTestConfig(
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
            WeightTestConfig(
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
        
        logger.info(f"✅ {len(self.weight_configs)} weight configurations created")
    
    def _create_fallback_systems(self):
        """Create additional fallback systems"""
        logger.info("🛡️ Creating additional fallback systems...")
        
        # Create keyword-based classifier
        self.keyword_classifier = self._create_keyword_classifier()
        
        # Create rule-based classifier
        self.rule_classifier = self._create_rule_classifier()
        
        logger.info("✅ Fallback systems created")
    
    def _create_keyword_classifier(self):
        """Create keyword-based classifier"""
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
        
        def classify_text(text):
            if not text:
                return {'label': 'unknown', 'confidence': 0.0, 'method': 'keyword'}
            
            text_lower = text.lower()
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
        
        return classify_text
    
    def _create_rule_classifier(self):
        """Create rule-based classifier"""
        def classify_text(text):
            if not text:
                return {'label': 'unknown', 'confidence': 0.0, 'method': 'rule'}
            
            text_lower = text.lower()
            
            # Rule-based classification
            if any(word in text_lower for word in ['satellite', 'landsat', 'sentinel', 'sensor']):
                return {'label': 'satellite_data', 'confidence': 0.8, 'method': 'rule'}
            elif any(word in text_lower for word in ['climate', 'weather', 'atmosphere']):
                return {'label': 'climate_data', 'confidence': 0.8, 'method': 'rule'}
            elif any(word in text_lower for word in ['geographic', 'coordinate', 'latitude']):
                return {'label': 'geospatial_data', 'confidence': 0.8, 'method': 'rule'}
            elif any(word in text_lower for word in ['time', 'temporal', 'historical']):
                return {'label': 'temporal_data', 'confidence': 0.8, 'method': 'rule'}
            elif any(word in text_lower for word in ['technical', 'specification', 'parameter']):
                return {'label': 'technical_data', 'confidence': 0.8, 'method': 'rule'}
            else:
                return {'label': 'general_data', 'confidence': 0.5, 'method': 'rule'}
        
        return classify_text
    
    def classify_text(self, text: str, config: WeightTestConfig = None) -> Dict[str, Any]:
        """Classify text using available systems"""
        if not text:
            return {'label': 'unknown', 'confidence': 0.0, 'method': 'empty_text'}
        
        # Use provided config or default
        if config is None:
            config = self.weight_configs[0]  # Use balanced config as default
        
        try:
            # Try BERT first
            if self.bert_available and config.max_tokens > 0:
                try:
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
                except Exception as e:
                    logger.warning(f"BERT classification failed: {e}")
            
            # Try fallback classifier
            if self.fallback_classifier:
                try:
                    prediction = self.fallback_classifier.predict([text])[0]
                    confidence = max(self.fallback_classifier.predict_proba([text])[0])
                    
                    return {
                        'label': prediction,
                        'confidence': confidence,
                        'method': 'fallback_tfidf'
                    }
                except Exception as e:
                    logger.warning(f"Fallback classifier failed: {e}")
            
            # Try keyword classifier
            if self.keyword_classifier:
                try:
                    return self.keyword_classifier(text)
                except Exception as e:
                    logger.warning(f"Keyword classifier failed: {e}")
            
            # Try rule classifier
            if self.rule_classifier:
                try:
                    return self.rule_classifier(text)
                except Exception as e:
                    logger.warning(f"Rule classifier failed: {e}")
            
            # Final fallback
            return {
                'label': 'general_data',
                'confidence': 0.3,
                'method': 'final_fallback'
            }
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            return {
                'label': 'error',
                'confidence': 0.0,
                'method': 'error'
            }
    
    def test_configuration(self, config: WeightTestConfig, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test a specific weight configuration"""
        logger.info(f"🧪 Testing configuration: {config.name}")
        
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
                logger.warning(f"Error processing item: {e}")
        
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
        
        result = {
            'config_name': config.name,
            'total_items': total_items,
            'successful_extractions': successful_extractions,
            'average_quality': average_quality,
            'average_confidence': average_confidence,
            'processing_time': processing_time,
            'memory_usage': memory_usage,
            'error_rate': error_rate,
            'unique_categories': unique_categories,
            'data_completeness': data_completeness,
            'bert_available': self.bert_available,
            'fallback_available': self.fallback_classifier is not None
        }
        
        self.test_results.append(result)
        self._save_test_result(result)
        
        logger.info(f"✅ Configuration {config.name} test completed:")
        logger.info(f"  - Success rate: {data_completeness:.2%}")
        logger.info(f"  - Average quality: {average_quality:.2f}")
        logger.info(f"  - Processing time: {processing_time:.2f}s")
        logger.info(f"  - Memory usage: {memory_usage:.1f}%")
        
        return result
    
    def _apply_weights(self, item: Dict[str, Any], config: WeightTestConfig) -> str:
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
    
    def _calculate_quality_score(self, item: Dict[str, Any], classification: Dict[str, Any], config: WeightTestConfig) -> float:
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
    
    def find_optimal_configuration(self, test_data: List[Dict[str, Any]]) -> WeightTestConfig:
        """Find the optimal configuration based on test results"""
        logger.info("🎯 Finding optimal configuration...")
        
        # Test all configurations
        for config in self.weight_configs:
            self.test_configuration(config, test_data)
        
        # Find best configuration based on composite score
        best_config = None
        best_score = 0.0
        
        for result in self.test_results:
            # Composite score calculation
            score = (
                result['average_quality'] * 0.3 +
                result['average_confidence'] * 0.2 +
                result['data_completeness'] * 0.2 +
                (1 - result['error_rate']) * 0.1 +
                (result['unique_categories'] / 10) * 0.1 -
                (result['processing_time'] / 100) * 0.1 -
                (result['memory_usage'] / 100) * 0.1
            )
            
            if score > best_score:
                best_score = score
                best_config = next(c for c in self.weight_configs if c.name == result['config_name'])
        
        if best_config:
            self.current_best_config = best_config
            logger.info(f"✅ Optimal configuration found: {best_config.name}")
            logger.info(f"📊 Composite score: {best_score:.3f}")
        
        return best_config
    
    def _save_test_result(self, result: Dict[str, Any]):
        """Save test result to file"""
        result_file = self.optimization_cache / f"test_result_{result['config_name']}.json"
        
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate optimization report"""
        if not self.test_results:
            return {"error": "No test results available"}
        
        report = {
            "total_configurations_tested": len(self.test_results),
            "best_configuration": self.current_best_config.name if self.current_best_config else None,
            "test_results": self.test_results,
            "system_info": {
                "bert_available": self.bert_available,
                "fallback_classifier_available": self.fallback_classifier is not None,
                "keyword_classifier_available": self.keyword_classifier is not None,
                "rule_classifier_available": self.rule_classifier is not None,
                "memory_usage": psutil.virtual_memory().percent,
                "cache_directory": str(self.optimization_cache)
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
            
            logger.info("✅ Cleanup completed")
            
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error: {e}")

def main():
    """Main function to test the BERT fix and weight optimizer"""
    logger.info("🚀 Starting BERT Fix and Weight Optimizer...")
    
    # Create optimizer
    optimizer = BERTFixAndWeightOptimizer()
    
    # Create sample test data
    test_data = [
        {"title": "Landsat 8 Satellite Imagery", "description": "High-resolution optical satellite data", "tags": "satellite, optical, remote sensing"},
        {"title": "Climate Data Collection", "description": "Atmospheric temperature and precipitation data", "tags": "climate, weather, atmosphere"},
        {"title": "Geographic Coordinate System", "description": "Spatial reference system for mapping", "tags": "geospatial, coordinate, mapping"},
        {"title": "Historical Time Series Data", "description": "Temporal analysis of environmental changes", "tags": "temporal, historical, time series"},
        {"title": "Technical Sensor Specifications", "description": "Detailed sensor parameters and metadata", "tags": "technical, sensor, specification"},
        {"title": "Disaster Monitoring System", "description": "Emergency response and hazard detection", "tags": "disaster, emergency, monitoring"},
        {"title": "Agricultural Crop Data", "description": "Vegetation monitoring and crop analysis", "tags": "agriculture, crop, vegetation"},
        {"title": "Urban Development Mapping", "description": "City infrastructure and population data", "tags": "urban, city, infrastructure"},
        {"title": "Oceanographic Data Collection", "description": "Marine science and coastal monitoring", "tags": "ocean, marine, coastal"},
        {"title": "Geological Survey Data", "description": "Mineral exploration and seismic analysis", "tags": "geology, mineral, seismic"}
    ]
    
    # Find optimal configuration
    optimal_config = optimizer.find_optimal_configuration(test_data)
    
    if optimal_config:
        print(f"\n🎉 Optimal configuration found: {optimal_config.name}")
        print(f"📊 Configuration details:")
        print(f"   - Title weight: {optimal_config.title_weight}")
        print(f"   - Description weight: {optimal_config.description_weight}")
        print(f"   - Quality threshold: {optimal_config.quality_threshold}")
        print(f"   - Max tokens: {optimal_config.max_tokens}")
        print(f"   - Memory limit: {optimal_config.memory_limit_mb}MB")
    
    # Generate report
    report = optimizer.get_optimization_report()
    print(f"\n📈 Optimization Report:")
    print(f"   - Configurations tested: {report['total_configurations_tested']}")
    print(f"   - BERT available: {report['system_info']['bert_available']}")
    print(f"   - Fallback available: {report['system_info']['fallback_classifier_available']}")
    print(f"   - Memory usage: {report['system_info']['memory_usage']:.1f}%")
    
    # Test individual classification
    print(f"\n🧪 Testing individual classification:")
    test_text = "NASA Landsat 8 satellite imagery with high resolution optical sensors"
    classification = optimizer.classify_text(test_text, optimal_config)
    print(f"   - Text: {test_text}")
    print(f"   - Classification: {classification}")
    
    optimizer.cleanup()
    
    print(f"\n✅ BERT Fix and Weight Optimizer completed successfully!")

if __name__ == "__main__":
    main() 