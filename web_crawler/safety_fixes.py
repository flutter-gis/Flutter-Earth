# Generated safety fixes for NoneType error prevention

# safe_get_pattern

# Safe .get() pattern
def safe_get(obj, key, default=None):
    """Safely get value from object, handling None cases."""
    if obj is None:
        return default
    elif isinstance(obj, dict):
        return obj.get(key, default)
    else:
        return default

# Usage: value = safe_get(result, 'title', '')

# safe_nested_get_pattern

# Safe nested .get() pattern
def safe_nested_get(obj, keys, default=None):
    """Safely get nested value from object."""
    result = obj
    for key in keys:
        if result is None:
            return default
        elif isinstance(result, dict):
            result = result.get(key)
        else:
            return default
    return result if result is not None else default

# Usage: label = safe_nested_get(result, ['ml_classification', 'enhanced_classification', 'label'], 'unknown')

# ui_component_safety

# UI component safety pattern
def safe_ui_call(component, method, *args, **kwargs):
    """Safely call UI component methods."""
    if component is not None and hasattr(component, method):
        try:
            return getattr(component, method)(*args, **kwargs)
        except Exception as e:
            logging.error(f"UI component {method} failed: {e}")
    return None

# Usage: safe_ui_call(self.console, 'append', 'message')

# ml_model_safety

# ML model safety pattern
def safe_ml_call(model, *args, **kwargs):
    """Safely call ML model."""
    if model is not None and hasattr(model, '__call__'):
        try:
            return model(*args, **kwargs)
        except Exception as e:
            logging.error(f"ML model call failed: {e}")
    return None

# Usage: result = safe_ml_call(self.bert_classifier, text)

# data_validation

# Data validation pattern
def validate_data_structure(data):
    """Validate data structure and provide defaults."""
    if data is None:
        return {
            'title': '',
            'description': '',
            'tags': [],
            'provider': '',
            'confidence_score': 0.0,
            'quality_score': 0.0
        }
    
    return {
        'title': data.get('title', ''),
        'description': data.get('description', ''),
        'tags': data.get('tags', []) if isinstance(data.get('tags'), list) else [],
        'provider': data.get('provider', ''),
        'confidence_score': data.get('confidence_score', 0.0),
        'quality_score': data.get('quality_score', 0.0)
    }

