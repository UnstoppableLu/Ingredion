from typing import Dict, Any
import re
import json

def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters
    text = re.sub(r'[^\w\s.,()-]', '', text)
    return text.strip()

def format_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Format and standardize extracted metrics."""
    formatted = {}
    
    for key, value in metrics.items():
        # Convert keys to snake_case
        formatted_key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
        
        # Ensure numeric values are properly typed
        if isinstance(value, str) and value.replace('.', '').isdigit():
            value = float(value) if '.' in value else int(value)
        
        formatted[formatted_key] = value
    
    return formatted

def save_metrics(metrics: Dict[str, Any], output_path: str) -> None:
    """Save extracted metrics to JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)
    except Exception as e:
        raise Exception(f"Error saving metrics: {str(e)}")