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
        """Get a classifier for the specified model"""
        model = self.load_model(model_name, model_type)
        if not model:
            return None
            
        if model_type == 'text_classification':
            return model['classifier']
        elif model_type == 'ner':
            return model['nlp']
        elif model_type == 'traditional_ml':
            return model
        else:
            return None
            
    def classify_text(self, text, model_name='distilbert-base-uncased', model_type='text_classification'):
        """Classify text using specified model"""
        classifier = self.get_classifier(model_name, model_type)
        if not classifier:
            return None
            
        try:
            if model_type == 'text_classification':
                result = classifier(
                    text,
                    truncation=True,
                    max_length=512,
                    return_all_scores=False
                )
                return result
                
            elif model_type == 'ner':
                doc = classifier(text)
                entities = [(ent.text, ent.label_) for ent in doc.ents]
                return entities
                
            elif model_type == 'traditional_ml':
                # Note: Traditional ML models need to be trained first
                return None
                
        except Exception as e:
            print(f"Classification error: {e}")
            return None
            
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