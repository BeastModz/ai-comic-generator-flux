import os

# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = True

# Ollama settings
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"  # Use a model that outputs proper JSON

# ComfyUI settings
COMFYUI_URL = "http://127.0.0.1:8000"
COMFYUI_WORKFLOW = "workflows/comic_workflow_api.json"  # API format workflow

# Output directories
OUTPUT_DIR = "output/comics"
TEMP_DIR = "output/temp"

# Comic generation settings
DEFAULT_STYLE = "anime"
DEFAULT_PANELS = 4
PANEL_WIDTH = 512
PANEL_HEIGHT = 768
