# AI Comic Generator Project

This is a Flask-based AI comic generator that integrates with local Ollama LLM and ComfyUI for creating comics from text descriptions.

## Project Structure
- `app.py` - Main Flask application with API routes
- `config.py` - Configuration settings for Ollama, ComfyUI, and app
- `services/` - Service modules for Ollama, ComfyUI, and comic generation
- `templates/` - HTML templates for the web interface
- `static/` - CSS, JavaScript, and other static assets
- `output/` - Generated comic images and temporary files

## Key Features
- Story panel generation using Ollama LLM
- Image generation via ComfyUI workflow
- Comic assembly with customizable layouts
- Web interface for easy comic creation
- Support for multiple art styles and panel configurations

## Dependencies
- Flask for web framework
- Requests for API communication
- Pillow for image processing
- Local Ollama server (port 11434)
- Local ComfyUI server (port 8188)

## Development Notes
- Uses modular service architecture
- RESTful API design
- Responsive web interface
- Error handling and logging
- Mock mode for testing without services
