"""
Dynamic model loader for model-service
Handles model loading from volume mounts or downloads from GitHub releases
"""
import os
import joblib
import requests
from pathlib import Path
import sys

# Configuration from environment
MODEL_DIR = os.getenv('MODEL_DIR', '/app/models')
MODEL_VERSION = os.getenv('MODEL_VERSION', 'latest')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'doda2025-team8/model-service')

class ModelLoader:
    """Handles loading and caching of ML models"""
    
    def __init__(self):
        self.model_dir = Path(MODEL_DIR)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.model = None
        self.preprocessor = None
        print(f"ModelLoader initialized with directory: {self.model_dir}")
        
    def get_model_path(self, model_name):
        """Get path to a specific model file"""
        return self.model_dir / f"{model_name}.joblib"
    
    def is_model_cached(self, model_name):
        """Check if model exists in cache"""
        cached = self.get_model_path(model_name).exists()
        if cached:
            size = self.get_model_path(model_name).stat().st_size
            print(f"  ✓ Found cached: {model_name}.joblib ({size:,} bytes)")
        return cached
    
    def download_model_from_github(self, model_name):
        """Download model from GitHub releases"""
        print(f"Downloading {model_name}.joblib (version: {MODEL_VERSION})...")
        
        # Construct GitHub release URL
        if MODEL_VERSION == 'latest':
            url = f"https://github.com/{GITHUB_REPO}/releases/latest/download/{model_name}.joblib"
        else:
            url = f"https://github.com/{GITHUB_REPO}/releases/download/{MODEL_VERSION}/{model_name}.joblib"
        
        print(f"  URL: {url}")
        
        try:
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Save to cache
            model_path = self.get_model_path(model_name)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"  Progress: {progress:.1f}% ({downloaded:,}/{total_size:,} bytes)", end='\r')
            
            print(f"\n  ✓ {model_name}.joblib downloaded successfully")
            return model_path
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"  ✗ Model not found at {url}")
                print(f"  Make sure you've released models using the GitHub workflow!")
                print(f"  Or mount models manually: docker run -v ./output:/app/models ...")
            raise RuntimeError(f"Failed to download model (HTTP {e.response.status_code}): {url}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Failed to download model from {url}: {e}")
    
    def load_model_file(self, model_name):
        """Load a model file (from cache or download if needed)"""
        # Check if model is in cache
        if not self.is_model_cached(model_name):
            print(f"  → {model_name}.joblib not found in {self.model_dir}")
            try:
                self.download_model_from_github(model_name)
            except Exception as e:
                print(f"\n{'='*60}")
                print(f"ERROR: Could not load {model_name}.joblib")
                print(f"{'='*60}")
                print(f"Reason: {e}")
                print(f"\nTroubleshooting:")
                print(f"1. Mount models manually:")
                print(f"   docker run -v /path/to/output:/app/models ...")
                print(f"2. Check GitHub releases:")
                print(f"   https://github.com/{GITHUB_REPO}/releases")
                print(f"3. Set correct MODEL_VERSION:")
                print(f"   docker run -e MODEL_VERSION=v1.0.0 ...")
                print(f"{'='*60}\n")
                sys.exit(1)
        else:
            print(f"Loading cached: {model_name}.joblib")
        
        # Load the model
        model_path = self.get_model_path(model_name)
        try:
            loaded = joblib.load(model_path)
            print(f"  ✓ {model_name}.joblib loaded successfully")
            return loaded
        except Exception as e:
            print(f"  ✗ Failed to load from {model_path}: {e}")
            raise RuntimeError(f"Failed to load model from {model_path}: {e}")
    
    def load_all_models(self):
        """Load all required models for the SMS classifier"""
        print("\n" + "="*60)
        print("Loading SMS Spam Classifier Models")
        print("="*60)
        
        print(f"\n[1/2] Loading preprocessor...")
        self.preprocessor = self.load_model_file('preprocessor')
        
        print(f"\n[2/2] Loading model...")
        self.model = self.load_model_file('model')
        
        print("\n" + "="*60)
        print("✓ All models loaded successfully!")
        print("="*60 + "\n")
        
        return {
            'preprocessor': self.preprocessor,
            'model': self.model
        }

# Global instance
model_loader = ModelLoader()