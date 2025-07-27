import os
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
from collections import OrderedDict
import pickle
import tempfile
import shutil

# Advanced ML imports
try:
    import torch
    import transformers
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification, 
        AutoModelForTokenClassification, pipeline,
        DistilBertTokenizer, DistilBertForSequenceClassification
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
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import SVC
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class ModelCache:
    """Advanced model caching system"""
    
    def __init__(self, cache_dir="model_cache", max_size_gb=5):
        self.cache_dir = cache_dir
        self.max_size_gb = max_size_gb
        self.cache_manifest_file = os.path.join(cache_dir, "manifest.json")
        self.cache_manifest = self._load_manifest()
        self.lock = threading.Lock()
        
        os.makedirs(cache_dir, exist_ok=True)
        
    def _load_manifest(self):
        """Load cache manifest"""
        if os.path.exists(self.cache_manifest_file):
            try:
                with open(self.cache_manifest_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def _save_manifest(self):
        """Save cache manifest"""
        with open(self.cache_manifest_file, 'w') as f:
            json.dump(self.cache_manifest, f, indent=2)
            
    def _get_cache_key(self, model_name, model_type, **kwargs):
        """Generate cache key for model"""
        key_data = f"{model_name}_{model_type}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def _get_cache_path(self, cache_key):
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
        
    def _get_cache_size(self):
        """Get total cache size in GB"""
        total_size = 0
        for root, dirs, files in os.walk(self.cache_dir):
            for file in files:
                if file.endswith('.pkl'):
                    total_size += os.path.getsize(os.path.join(root, file))
        return total_size / (1024**3)
        
    def _cleanup_cache(self):
        """Clean up old cache entries if size exceeds limit"""
        if self._get_cache_size() <= self.max_size_gb:
            return
            
        # Sort by last access time
        sorted_entries = sorted(
            self.cache_manifest.items(),
            key=lambda x: x[1]['last_access']
        )
        
        # Remove oldest entries
        for cache_key, info in sorted_entries:
            cache_path = self._get_cache_path(cache_key)
            if os.path.exists(cache_path):
                os.remove(cache_path)
                del self.cache_manifest[cache_key]
                
            if self._get_cache_size() <= self.max_size_gb * 0.8:  # Leave 20% buffer
                break
                
        self._save_manifest()
        
    def get_model(self, model_name, model_type, **kwargs):
        """Get model from cache or load it"""
        cache_key = self._get_cache_key(model_name, model_type, **kwargs)
        
        with self.lock:
            # Check if model is in cache
            if cache_key in self.cache_manifest:
                cache_path = self._get_cache_path(cache_key)
                if os.path.exists(cache_path):
                    try:
                        with open(cache_path, 'rb') as f:
                            model = pickle.load(f)
                        # Update last access time
                        self.cache_manifest[cache_key]['last_access'] = datetime.now().isoformat()
                        self._save_manifest()
                        return model
                    except:
                        # Remove corrupted cache entry
                        del self.cache_manifest[cache_key]
                        if os.path.exists(cache_path):
                            os.remove(cache_path)
                            
            return None
            
    def save_model(self, model, model_name, model_type, **kwargs):
        """Save model to cache"""
        if not TRANSFORMERS_AVAILABLE:
            return
            
        cache_key = self._get_cache_key(model_name, model_type, **kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        with self.lock:
            try:
                # Save model
                with open(cache_path, 'wb') as f:
                    pickle.dump(model, f)
                    
                # Update manifest
                self.cache_manifest[cache_key] = {
                    'model_name': model_name,
                    'model_type': model_type,
                    'kwargs': kwargs,
                    'size_mb': os.path.getsize(cache_path) / (1024**2),
                    'created': datetime.now().isoformat(),
                    'last_access': datetime.now().isoformat()
                }
                
                self._save_manifest()
                self._cleanup_cache()
                
            except Exception as e:
                print(f"Failed to cache model: {e}")

class AdvancedMLManager:
    """Advanced ML model manager with multiple models and caching"""
    
    def __init__(self):
        self.model_cache = ModelCache()
        self.models = {}
        self.classifiers = {}
        self.loading_models = set()
        self.model_lock = threading.Lock()
        
        # Model configurations
        self.model_configs = {
            'text_classification': {
                'distilbert-base-uncased': {
                    'type': 'transformer',
                    'max_length': 512,
                    'num_labels': 5,
                    'device': -1  # CPU
                },
                'bert-base-uncased': {
                    'type': 'transformer',
                    'max_length': 512,
                    'num_labels': 5,
                    'device': -1
                }
            },
            'ner': {
                'en_core_web_sm': {
                    'type': 'spacy',
                    'language': 'en'
                },
                'en_core_web_md': {
                    'type': 'spacy',
                    'language': 'en'
                }
            },
            'traditional_ml': {
                'tfidf_rf': {
                    'type': 'sklearn',
                    'vectorizer': 'tfidf',
                    'classifier': 'random_forest'
                },
                'tfidf_nb': {
                    'type': 'sklearn',
                    'vectorizer': 'tfidf',
                    'classifier': 'naive_bayes'
                }
            }
        }
        
    def load_model(self, model_name, model_type, force_reload=False):
        """Load a model with caching"""
        model_key = f"{model_type}_{model_name}"
        
        with self.model_lock:
            if model_key in self.loading_models:
                return None  # Already loading
                
            if model_key in self.models and not force_reload:
                return self.models[model_key]
                
            self.loading_models.add(model_key)
            
        try:
            # Try to get from cache first
            if not force_reload:
                cached_model = self.model_cache.get_model(model_name, model_type)
                if cached_model:
                    with self.model_lock:
                        self.models[model_key] = cached_model
                        self.loading_models.discard(model_key)
                    return cached_model
                    
            # Load model based on type
            if model_type == 'text_classification':
                model = self._load_transformer_model(model_name)
            elif model_type == 'ner':
                model = self._load_spacy_model(model_name)
            elif model_type == 'traditional_ml':
                model = self._load_sklearn_model(model_name)
            else:
                raise ValueError(f"Unknown model type: {model_type}")
                
            # Cache the model
            if model:
                self.model_cache.save_model(model, model_name, model_type)
                
            with self.model_lock:
                self.models[model_key] = model
                self.loading_models.discard(model_key)
                
            return model
            
        except Exception as e:
            with self.model_lock:
                self.loading_models.discard(model_key)
            print(f"Failed to load model {model_name}: {e}")
            return None
            
    def _load_transformer_model(self, model_name):
        """Load transformer model"""
        if not TRANSFORMERS_AVAILABLE:
            return None
            
        config = self.model_configs['text_classification'].get(model_name, {})
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, use_auth_token=False, revision="main")
            model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=config.get('num_labels', 5),
                trust_remote_code=True,
                use_auth_token=False,
                revision="main"
            )
            
            classifier = pipeline(
                "text-classification",
                model=model,
                tokenizer=tokenizer,
                device=config.get('device', -1)
            )
            
            return {
                'tokenizer': tokenizer,
                'model': model,
                'classifier': classifier,
                'config': config
            }
            
        except Exception as e:
            print(f"Failed to load transformer model {model_name}: {e}")
            return None
            
    def _load_spacy_model(self, model_name):
        """Load spaCy model"""
        if not SPACY_AVAILABLE:
            return None
            
        try:
            nlp = spacy.load(model_name)
            return {
                'nlp': nlp,
                'config': self.model_configs['ner'].get(model_name, {})
            }
        except Exception as e:
            print(f"Failed to load spaCy model {model_name}: {e}")
            return None
            
    def _load_sklearn_model(self, model_name):
        """Load scikit-learn model"""
        if not SKLEARN_AVAILABLE:
            return None
            
        config = self.model_configs['traditional_ml'].get(model_name, {})
        
        try:
            # Initialize vectorizer
            if config.get('vectorizer') == 'tfidf':
                vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
            else:
                vectorizer = None
                
            # Initialize classifier
            if config.get('classifier') == 'random_forest':
                classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            elif config.get('classifier') == 'naive_bayes':
                classifier = MultinomialNB()
            elif config.get('classifier') == 'svm':
                classifier = SVC(probability=True, random_state=42)
            else:
                classifier = None
                
            return {
                'vectorizer': vectorizer,
                'classifier': classifier,
                'config': config,
                'fitted': False
            }
            
        except Exception as e:
            print(f"Failed to load sklearn model {model_name}: {e}")
            return None
            
    def get_classifier(self, model_name, model_type):
        """Get a classifier with enhanced caching and fallback"""
        model_key = f"{model_type}_{model_name}"
        
        if model_key in self.classifiers:
            return self.classifiers[model_key]
        
        # Try to load the model
        model = self.load_model(model_name, model_type)
        if model:
            self.classifiers[model_key] = model
            return model
        
            return None
            
    def classify_text(self, text, model_name='distilbert-base-uncased', model_type='text_classification'):
        """Enhanced text classification with multiple models and ensemble methods"""
        results = {
            'primary_classification': None,
            'ensemble_results': {},
            'confidence_scores': {},
            'model_metadata': {}
        }
        
        try:
            # Get the primary classifier
            classifier = self.get_classifier(model_name, model_type)
            if classifier:
                if model_type == 'text_classification' and TRANSFORMERS_AVAILABLE:
                    # Enhanced BERT classification
                    bert_result = classifier(
                        text[:512],  # Limit length for efficiency
                    truncation=True,
                        max_length=256,
                        return_all_scores=True
                    )
                    
                    if isinstance(bert_result, list) and len(bert_result) > 0:
                        # Sort by confidence
                        sorted_results = sorted(bert_result[0], key=lambda x: x['score'], reverse=True)
                        results['primary_classification'] = {
                            'label': sorted_results[0]['label'],
                            'confidence': sorted_results[0]['score'],
                            'top_3_predictions': sorted_results[:3],
                            'all_scores': sorted_results
                        }
                        
                        # Calculate confidence distribution
                        results['confidence_scores'] = {
                            'max_confidence': sorted_results[0]['score'],
                            'avg_confidence': sum(r['score'] for r in sorted_results) / len(sorted_results),
                            'confidence_variance': self._calculate_variance([r['score'] for r in sorted_results])
                        }
                
                elif model_type == 'ner' and SPACY_AVAILABLE:
                    # Enhanced spaCy NER
                    doc = classifier(text[:1000])
                    entities = {}
                    for ent in doc.ents:
                        if ent.label_ not in entities:
                            entities[ent.label_] = []
                        if ent.text not in entities[ent.label_]:
                            entities[ent.label_].append(ent.text)
                    
                    results['primary_classification'] = {
                        'entities': entities,
                        'entity_count': len(doc.ents),
                        'entity_types': list(entities.keys())
                    }
                
                # Add model metadata
                results['model_metadata'] = {
                    'model_name': model_name,
                    'model_type': model_type,
                    'text_length': len(text),
                    'processing_timestamp': datetime.now().isoformat()
                }
            
            # Apply ensemble methods if multiple models are available
            results['ensemble_results'] = self._apply_ensemble_classification(text)
            
        except Exception as e:
            print(f"Classification failed: {e}")
            results['error'] = str(e)
        
        return results
    
    def _calculate_variance(self, scores):
        """Calculate variance of confidence scores"""
        if len(scores) < 2:
            return 0.0
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance
    
    def _apply_ensemble_classification(self, text):
        """Apply ensemble classification using multiple models"""
        ensemble_results = {}
        
        try:
            # Collect predictions from all available models
            predictions = []
            
            # BERT predictions
            if 'distilbert-base-uncased' in self.models:
                bert_classifier = self.models.get('text_classification_distilbert-base-uncased')
                if bert_classifier:
                    try:
                        bert_result = bert_classifier(text[:256], truncation=True, return_all_scores=True)
                        if isinstance(bert_result, list) and len(bert_result) > 0:
                            predictions.append({
                                'model': 'bert',
                                'predictions': bert_result[0],
                                'weight': 0.4
                            })
                    except Exception as e:
                        print(f"BERT ensemble prediction failed: {e}")
            
            # spaCy predictions
            if 'en_core_web_sm' in self.models:
                spacy_model = self.models.get('ner_en_core_web_sm')
                if spacy_model:
                    try:
                        doc = spacy_model(text[:1000])
                        entity_scores = {}
                        for ent in doc.ents:
                            entity_scores[ent.label_] = entity_scores.get(ent.label_, 0) + 1
                        
                        # Convert entity counts to scores
                        total_entities = len(doc.ents)
                        if total_entities > 0:
                            entity_predictions = [
                                {'label': label, 'score': count / total_entities}
                                for label, count in entity_scores.items()
                            ]
                            predictions.append({
                                'model': 'spacy',
                                'predictions': entity_predictions,
                                'weight': 0.3
                            })
                    except Exception as e:
                        print(f"spaCy ensemble prediction failed: {e}")
            
            # Traditional ML predictions
            if SKLEARN_AVAILABLE and self.vectorizers.get('tfidf'):
                try:
                    # Use TF-IDF for traditional ML classification
                    X = self.vectorizers['tfidf'].transform([text])
                    
                    for name, classifier in self.classifiers.items():
                        if hasattr(classifier, 'predict_proba'):
                            try:
                                proba = classifier.predict_proba(X)[0]
                                labels = getattr(classifier, 'classes_', [f'class_{i}' for i in range(len(proba))])
                                ml_predictions = [
                                    {'label': label, 'score': score}
                                    for label, score in zip(labels, proba)
                                ]
                                predictions.append({
                                    'model': f'sklearn_{name}',
                                    'predictions': ml_predictions,
                                    'weight': 0.2
                                })
                            except Exception as e:
                                print(f"Sklearn classifier {name} failed: {e}")
                except Exception as e:
                    print(f"Traditional ML ensemble prediction failed: {e}")
            
            # Combine predictions using weighted voting
            if predictions:
                ensemble_results = self._combine_predictions(predictions)
                
        except Exception as e:
            print(f"Ensemble classification failed: {e}")
            ensemble_results['error'] = str(e)
        
        return ensemble_results
    
    def _combine_predictions(self, predictions):
        """Combine predictions from multiple models using weighted voting"""
        combined_scores = {}
        total_weight = 0
        
        for pred in predictions:
            weight = pred.get('weight', 1.0)
            total_weight += weight
            
            for p in pred['predictions']:
                label = p['label']
                score = p['score']
                
                if label not in combined_scores:
                    combined_scores[label] = {'weighted_sum': 0, 'total_weight': 0}
                
                combined_scores[label]['weighted_sum'] += score * weight
                combined_scores[label]['total_weight'] += weight
        
        # Calculate final weighted scores
        final_predictions = []
        for label, score_info in combined_scores.items():
            if score_info['total_weight'] > 0:
                final_score = score_info['weighted_sum'] / score_info['total_weight']
                final_predictions.append({
                    'label': label,
                    'score': final_score,
                    'contributing_models': len([p for p in predictions if any(pred['label'] == label for pred in p['predictions'])])
                })
        
        # Sort by score
        final_predictions.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'ensemble_predictions': final_predictions,
            'top_prediction': final_predictions[0] if final_predictions else None,
            'total_models': len(predictions),
            'total_weight': total_weight,
            'prediction_confidence': self._calculate_ensemble_confidence(final_predictions)
        }
    
    def _calculate_ensemble_confidence(self, predictions):
        """Calculate confidence metrics for ensemble predictions"""
        if not predictions:
            return {'overall_confidence': 0.0, 'agreement_score': 0.0}
        
        # Overall confidence based on top prediction
        top_score = predictions[0]['score']
        
        # Agreement score based on how many models contributed
        total_contributions = sum(p['contributing_models'] for p in predictions)
        max_possible_contributions = len(predictions) * 3  # Assume 3 models max
        agreement_score = total_contributions / max_possible_contributions if max_possible_contributions > 0 else 0
        
        return {
            'overall_confidence': top_score,
            'agreement_score': agreement_score,
            'prediction_strength': 'high' if top_score > 0.7 else 'medium' if top_score > 0.5 else 'low'
        }
            
    def get_available_models(self):
        """Get list of available models"""
        available = {}
        
        for model_type, models in self.model_configs.items():
            available[model_type] = []
            for model_name in models.keys():
                model_key = f"{model_type}_{model_name}"
                if model_key in self.models:
                    available[model_type].append({
                        'name': model_name,
                        'loaded': True,
                        'cached': True
                    })
                else:
                    available[model_type].append({
                        'name': model_name,
                        'loaded': False,
                        'cached': False
                    })
                    
        return available
        
    def preload_models(self, model_list):
        """Preload multiple models in background"""
        def preload_worker():
            for model_type, model_name in model_list:
                self.load_model(model_name, model_type)
                
        thread = threading.Thread(target=preload_worker, daemon=True)
        thread.start()
        return thread

# Global ML manager instance
ml_manager = AdvancedMLManager() 